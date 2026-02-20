from django.shortcuts import render, redirect
from apps.main.home.decorator import conditional_otp_required
from .models import Friendship
from apps.main.home.models import User
from django.db.models import Q

from django.http import JsonResponse

from utils.notifications import send_notification
from utils.push import send_push_for_event, EVENT_CONVITE_AMIZADE
from django.urls import reverse

from apps.main.home.models import PerfilGamer, ConquistaUsuario
from django.contrib import messages

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.vary import vary_on_cookie

import logging

from core.log_utils import log_action

logger = logging.getLogger(__name__)


# Função movida para o consumer WebSocket


@conditional_otp_required
def message(request):
    accepted_friendships = Friendship.objects.filter(user=request.user, accepted=True)
    
    if request.user.avatar:
        user_uuid = request.user.uuid
    else:
        user_uuid = None

    context = {
        'segment': 'index',
        'parent': 'message',
        'accepted_friendships': accepted_friendships,
        'user_uuid': user_uuid,
        'username': request.user.username,
    }
    return render(request, 'pages/chat.html', context)


@conditional_otp_required
def send_friend_request(request, user_id):
    friend = User.objects.get(id=user_id)

    # Verifica se já são amigos
    if Friendship.objects.filter(user=request.user, friend=friend, accepted=True).exists():
        return redirect('message:friends_list')

    # Verifica se um pedido de amizade já foi enviado
    if Friendship.objects.filter(user=request.user, friend=friend, accepted=False).exists():
        return redirect('message:friends_list')

    # Verifica se o amigo já enviou um pedido de amizade para o usuário
    if Friendship.objects.filter(user=friend, friend=request.user, accepted=False).exists():
        return redirect('message:friends_list')

    Friendship.objects.create(user=request.user, friend=friend)
    log_action(logger, "message_amizade", "pedido_enviado", user=request.user.username, friend=friend.username)

    # Ganha XP e verifica conquista
    if request.user.is_authenticated:
        perfil = PerfilGamer.objects.get(user=request.user)

        # Só dá XP se for o primeiro pedido de amizade
        if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='primeiro_amigo').exists():
            perfil.adicionar_xp(30)
            messages.success(request, "Você enviou seu primeiro pedido de amizade! +30 XP")

    try:
        message = f"{request.user.username} enviou um pedido de amizade."
        link = reverse('message:friends_list')
        send_notification(
            user=friend,
            notification_type='user',
            message=message,
            created_by=request.user,
            link=link
        )
        send_push_for_event(
            friend,
            EVENT_CONVITE_AMIZADE,
            url=link,
            username=request.user.username,
            async_send=True,
        )
    except Exception as e:
        logger.error(f"Erro ao criar notificação: {str(e)}")

    return redirect('message:friends_list')


@conditional_otp_required
def accept_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)

    friendship.accepted = True
    friendship.save()
    Friendship.objects.get_or_create(user=friendship.friend, friend=friendship.user, accepted=True)
    log_action(logger, "message_amizade", "aceito", user=request.user.username, friend=friendship.user.username if friendship.friend == request.user else friendship.friend.username)

    # Ganha XP e verifica conquistas
    if request.user.is_authenticated:
        perfil = PerfilGamer.objects.get(user=request.user)

        # Só dá XP se for o primeiro pedido de amizade aceito
        if not ConquistaUsuario.objects.filter(usuario=request.user, conquista__codigo='primeiro_amigo_aceito').exists():
            perfil.adicionar_xp(40)
            messages.success(request, "Você aceitou seu primeiro pedido de amizade! +40 XP")

    return redirect('message:friends_list')


@conditional_otp_required
def reject_friend_request(request, friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)
    requester = friendship.user.username
    target = friendship.friend.username
    friendship.delete()
    log_action(logger, "message_amizade", "recusado", user=request.user.username, requester=requester, target=target)
    return redirect('message:friends_list')


@conditional_otp_required
def cancel_friend_request(request, friendship_id):
    """
    Cancela uma solicitação de amizade enviada pelo usuário
    """
    try:
        friendship = Friendship.objects.get(
            id=friendship_id,
            user=request.user,  # Apenas o usuário que enviou pode cancelar
            accepted=False
        )
        friendship.delete()
        messages.success(request, "Solicitação de amizade cancelada com sucesso.")
    except Friendship.DoesNotExist:
        messages.error(request, "Solicitação de amizade não encontrada.")
    
    return redirect('message:friends_list')


@conditional_otp_required
def remove_friend(request, friendship_id):
    try:
        # Obtém a amizade
        friendship = Friendship.objects.get(id=friendship_id)

        # Verifica se o usuário é parte da amizade
        if friendship.user == request.user or friendship.friend == request.user:
            # Remove a amizade para ambos os lados
            friendship.delete()  # Remove a amizade

            # Remove a amizade bidirecional
            Friendship.objects.filter(
                (Q(user=friendship.friend) & Q(friend=friendship.user)) |
                (Q(user=friendship.user) & Q(friend=friendship.friend))
            ).delete()

    except Friendship.DoesNotExist:
        pass  # Caso não exista, não faz nada

    return redirect('message:friends_list')


@conditional_otp_required
@vary_on_cookie
def friends_list(request):
    """
    View otimizada para lista de amigos com paginação e filtros
    """
    # Parâmetros de paginação e filtros
    page = request.GET.get('page', 1)
    search_query = request.GET.get('search', '').strip()
    friends_per_page = 20  # Limite de amigos por página
    users_per_page = 30    # Limite de usuários por página
    
    # Amigos aceitos - otimizado com select_related
    accepted_friendships = Friendship.objects.filter(
        user=request.user, 
        accepted=True
    ).select_related('friend')
    
    # Solicitações de amizade pendentes recebidas
    pending_friend_requests = Friendship.objects.filter(
        friend=request.user, 
        accepted=False
    ).select_related('user')
    
    # Solicitações de amizade enviadas
    sent_friend_requests = Friendship.objects.filter(
        user=request.user, 
        accepted=False
    ).select_related('friend')
    
    # Query base para usuários disponíveis
    users_queryset = User.objects.exclude(id=request.user.id)
    
    # Excluir usuários que já são amigos ou têm solicitações pendentes
    excluded_user_ids = set()
    
    # IDs de amigos aceitos
    excluded_user_ids.update(
        accepted_friendships.values_list('friend_id', flat=True)
    )
    
    # IDs de solicitações enviadas
    excluded_user_ids.update(
        sent_friend_requests.values_list('friend_id', flat=True)
    )
    
    # IDs de solicitações recebidas
    excluded_user_ids.update(
        pending_friend_requests.values_list('user_id', flat=True)
    )
    
    users_queryset = users_queryset.exclude(id__in=excluded_user_ids)
    
    # Aplicar filtro de busca se fornecido
    if search_query:
        users_queryset = users_queryset.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Ordenar por nome de usuário
    users_queryset = users_queryset.order_by('username')
    
    # Paginação para usuários disponíveis
    users_paginator = Paginator(users_queryset, users_per_page)
    
    try:
        users_page = users_paginator.page(page)
    except PageNotAnInteger:
        users_page = users_paginator.page(1)
    except EmptyPage:
        users_page = users_paginator.page(users_paginator.num_pages)
    
    # Paginação para amigos aceitos (se houver muitos)
    if accepted_friendships.count() > friends_per_page:
        friends_paginator = Paginator(accepted_friendships, friends_per_page)
        friends_page = request.GET.get('friends_page', 1)
        try:
            accepted_friendships = friends_paginator.page(friends_page)
        except (PageNotAnInteger, EmptyPage):
            accepted_friendships = friends_paginator.page(1)
    
    # Paginação para solicitações pendentes (se houver muitas)
    pending_per_page = 10
    if pending_friend_requests.count() > pending_per_page:
        pending_paginator = Paginator(pending_friend_requests, pending_per_page)
        pending_page = request.GET.get('pending_page', 1)
        try:
            pending_friend_requests = pending_paginator.page(pending_page)
        except (PageNotAnInteger, EmptyPage):
            pending_friend_requests = pending_paginator.page(1)
    
    # Estatísticas para o template
    # Contar total antes da paginação
    total_pending = Friendship.objects.filter(friend=request.user, accepted=False).count()
    total_sent = Friendship.objects.filter(user=request.user, accepted=False).count()
    
    stats = {
        'total_friends': accepted_friendships.count() if not hasattr(accepted_friendships, 'paginator') else accepted_friendships.paginator.count,
        'total_pending_requests': total_pending,
        'total_sent_requests': total_sent,
        'total_available_users': users_paginator.count,
        'search_query': search_query,
    }
    
    from utils.pagination_helper import prepare_pagination_context
    
    # Prepara paginação para friends (se for paginado)
    friends_pagination_context = {}
    if hasattr(accepted_friendships, 'paginator'):
        friends_pagination = prepare_pagination_context(accepted_friendships)
        friends_pagination_context = {
            'friends_current_page': accepted_friendships.number,
            'friends_total_pages': accepted_friendships.paginator.num_pages,
            'friends_has_previous': accepted_friendships.has_previous(),
            'friends_has_next': accepted_friendships.has_next(),
            'friends_previous_page_number': accepted_friendships.previous_page_number() if accepted_friendships.has_previous() else None,
            'friends_next_page_number': accepted_friendships.next_page_number() if accepted_friendships.has_next() else None,
            'friends_page_range': friends_pagination.get('page_range', []),
            'friends_show_first': friends_pagination.get('show_first', False),
            'friends_show_last': friends_pagination.get('show_last', False),
            'friends_show_first_ellipsis': friends_pagination.get('show_first_ellipsis', False),
            'friends_show_last_ellipsis': friends_pagination.get('show_last_ellipsis', False),
        }
    
    # Prepara paginação para users
    users_pagination = prepare_pagination_context(users_page)
    
    context = {
        'accepted_friendships': accepted_friendships,
        'pending_friend_requests': pending_friend_requests,
        'sent_friend_requests': sent_friend_requests,
        'users': users_page,
        **friends_pagination_context,
        'users_current_page': users_page.number,
        'users_total_pages': users_page.paginator.num_pages,
        'users_has_previous': users_page.has_previous(),
        'users_has_next': users_page.has_next(),
        'users_previous_page_number': users_page.previous_page_number() if users_page.has_previous() else None,
        'users_next_page_number': users_page.next_page_number() if users_page.has_next() else None,
        'users_page_range': users_pagination.get('page_range', []),
        'users_show_first': users_pagination.get('show_first', False),
        'users_show_last': users_pagination.get('show_last', False),
        'users_show_first_ellipsis': users_pagination.get('show_first_ellipsis', False),
        'users_show_last_ellipsis': users_pagination.get('show_last_ellipsis', False),
        'stats': stats,
        'segment': 'friend-list',
        'parent': 'message',
    }
    
    return render(request, 'pages/friends.html', context)


# Endpoints AJAX removidos - agora usando WebSocket


@conditional_otp_required
def search_users_ajax(request):
    """
    View AJAX para busca de usuários em tempo real
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    
    if not search_query or len(search_query) < 2:
        return JsonResponse({'users': [], 'has_next': False, 'total': 0})
    
    # Buscar usuários que não são amigos nem têm solicitações pendentes
    excluded_user_ids = set()
    
    # IDs de amigos aceitos
    accepted_friendships = Friendship.objects.filter(
        user=request.user, 
        accepted=True
    ).values_list('friend_id', flat=True)
    excluded_user_ids.update(accepted_friendships)
    
    # IDs de solicitações enviadas
    sent_requests = Friendship.objects.filter(
        user=request.user, 
        accepted=False
    ).values_list('friend_id', flat=True)
    excluded_user_ids.update(sent_requests)
    
    # IDs de solicitações recebidas
    received_requests = Friendship.objects.filter(
        friend=request.user, 
        accepted=False
    ).values_list('user_id', flat=True)
    excluded_user_ids.update(received_requests)
    
    # Query de busca
    users_queryset = User.objects.exclude(
        id=request.user.id
    ).exclude(
        id__in=excluded_user_ids
    ).filter(
        Q(username__icontains=search_query) |
        Q(first_name__icontains=search_query) |
        Q(last_name__icontains=search_query)
    ).order_by('username')[:10]  # Limitar a 10 resultados
    
    # Serializar resultados
    users_data = []
    for user in users_queryset:
        users_data.append({
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'bio': user.bio or '',
            'is_email_verified': user.is_email_verified,
            'fichas': user.fichas,
            'has_avatar': bool(user.avatar),
            'uuid': str(user.uuid) if user.uuid else None,
        })
    
    return JsonResponse({
        'users': users_data,
        'total': len(users_data),
        'query': search_query
    })



