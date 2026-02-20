from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.db import models
from apps.main.home.decorator import conditional_otp_required
from .models import Notification, PublicNotificationView, PushSubscription, PushNotificationLog, NotificationReward, PublicNotificationRewardClaim
from utils.notifications import claim_notification_rewards
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from pywebpush import webpush, WebPushException
import logging

from core.log_utils import log_action

logger = logging.getLogger(__name__)


@conditional_otp_required
def get_notifications(request):
    # Notificações privadas do usuário (exclui staff se user não for staff/superuser)
    # Inclui notificações não visualizadas OU notificações com prêmios não reclamados
    user_notifications = Notification.objects.filter(
        user=request.user
    ).exclude(
        notification_type='staff'
    ).filter(
        models.Q(viewed=False) | models.Q(rewards__isnull=False, rewards_claimed=False)
    ).distinct().order_by('-created_at')

    if request.user.is_staff or request.user.is_superuser:
        # Se for staff/superuser, incluir também notificações staff pra ele
        staff_notifications = Notification.objects.filter(
            user=request.user,
            notification_type='staff'
        ).filter(
            models.Q(viewed=False) | models.Q(rewards__isnull=False, rewards_claimed=False)
        ).distinct().order_by('-created_at')
        user_notifications = user_notifications | staff_notifications

    # Notificações públicas
    public_notifications = Notification.objects.filter(
        user=None,
        created_at__gte=request.user.date_joined
    ).order_by('-created_at')

    # Filtra notificações públicas staff apenas para usuários staff/superusers
    if not (request.user.is_staff or request.user.is_superuser):
        public_notifications = public_notifications.exclude(notification_type='staff')

    # Visualizações públicas
    public_notifications_viewed = PublicNotificationView.objects.filter(user=request.user, viewed=True)
    public_notifications_viewed_ids = [pnv.notification.id for pnv in public_notifications_viewed]

    # Prêmios públicos já reclamados por este usuário
    public_rewards_claimed = PublicNotificationRewardClaim.objects.filter(user=request.user)
    public_rewards_claimed_ids = set([prc.notification.id for prc in public_rewards_claimed])

    notifications_list = []

    # Notificações privadas
    for notification in user_notifications.select_related().prefetch_related('rewards'):
        rewards_data = []
        for reward in notification.rewards.all():
            reward_dict = {
                'item_id': reward.item_id,
                'item_name': reward.item_name,
                'item_enchant': reward.item_enchant,
                'item_amount': reward.item_amount,
                'fichas_amount': reward.fichas_amount or 0,
            }
            rewards_data.append(reward_dict)
        
        has_rewards = notification.rewards.exists()
        rewards_claimed = notification.rewards_claimed
        rewards_expired = notification.rewards_expired()
        has_unclaimed_rewards = has_rewards and not rewards_claimed and not rewards_expired
        
        notifications_list.append({
            'id': notification.id,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'viewed': notification.viewed,
            'detail_url': reverse('notification:notification_detail', args=[notification.id]),
            'has_rewards': has_rewards,
            'rewards_claimed': rewards_claimed,
            'rewards_expired': rewards_expired,
            'rewards_expires_at': notification.rewards_expires_at.strftime('%Y-%m-%d %H:%M:%S') if notification.rewards_expires_at else None,
            'has_unclaimed_rewards': has_unclaimed_rewards,
            'rewards': rewards_data,
        })

    # Notificações públicas
    # Inclui notificações não visualizadas OU com prêmios não reclamados (e não expirados)
    for notification in public_notifications.select_related().prefetch_related('rewards'):
        has_rewards = notification.rewards.exists()
        rewards_expired = notification.rewards_expired()
        # Para notificações públicas, verifica se este usuário específico já reclamou
        user_claimed = notification.id in public_rewards_claimed_ids
        has_unclaimed_rewards = has_rewards and not user_claimed and not rewards_expired
        is_unviewed = notification.id not in public_notifications_viewed_ids
        
        if is_unviewed or has_unclaimed_rewards:
            rewards_data = []
            for reward in notification.rewards.all():
                reward_dict = {
                    'item_id': reward.item_id,
                    'item_name': reward.item_name,
                    'item_enchant': reward.item_enchant,
                    'item_amount': reward.item_amount,
                    'fichas_amount': reward.fichas_amount or 0,
                }
                rewards_data.append(reward_dict)
            
            rewards_expired = notification.rewards_expired()
            has_unclaimed_rewards = has_rewards and not user_claimed and not rewards_expired
            
            notifications_list.append({
                'id': notification.id,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'viewed': not is_unviewed,
                'detail_url': reverse('notification:notification_detail', args=[notification.id]),
                'has_rewards': has_rewards,
                'rewards_claimed': user_claimed,
                'rewards_expired': rewards_expired,
                'rewards_expires_at': notification.rewards_expires_at.strftime('%Y-%m-%d %H:%M:%S') if notification.rewards_expires_at else None,
                'has_unclaimed_rewards': has_unclaimed_rewards,
                'rewards': rewards_data,
            })

    return JsonResponse({'notifications': notifications_list})


@conditional_otp_required
def mark_all_as_read(request):
    # Marcar todas as notificações privadas como lidas
    Notification.objects.filter(user=request.user, viewed=False).update(viewed=True)

    # Buscar notificações públicas válidas para este usuário
    public_notifications = Notification.objects.filter(
        user=None,
        created_at__gte=request.user.date_joined
    )

    if not (request.user.is_staff or request.user.is_superuser):
        public_notifications = public_notifications.exclude(notification_type='staff')

    for notification in public_notifications:
        public_notification_view, created = PublicNotificationView.objects.get_or_create(
            user=request.user,
            notification=notification
        )
        if not public_notification_view.viewed:
            public_notification_view.viewed = True
            public_notification_view.save()

    return JsonResponse({'status': 'ok'})


@conditional_otp_required
def clear_all_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({'status': 'ok'})


@conditional_otp_required
def notification_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    # Proteção: usuário comum tentando acessar notificação staff
    if notification.notification_type == 'staff' and not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'error': 'Você não tem permissão para ver esta notificação.'}, status=400)

    # Garante que só o dono (ou notificação pública) pode visualizar
    if notification.user == request.user:
        notification.viewed = True
        notification.save()

    elif notification.user is None:
        public_notification_view = PublicNotificationView.objects.filter(
            user=request.user,
            notification=notification
        ).first()
        if not public_notification_view:
            PublicNotificationView.objects.create(
                user=request.user,
                notification=notification,
                viewed=True
            )

    else:
        return JsonResponse({'error': 'Você não tem permissão para ver esta notificação.'}, status=400)

    # Busca prêmios relacionados
    rewards_data = []
    for reward in notification.rewards.all():
        reward_dict = {
            'item_id': reward.item_id,
            'item_name': reward.item_name,
            'item_enchant': reward.item_enchant,
            'item_amount': reward.item_amount,
            'fichas_amount': reward.fichas_amount or 0,
        }
        rewards_data.append(reward_dict)

    has_rewards = notification.rewards.exists()
    rewards_expired = notification.rewards_expired()
    # Para notificações públicas, verifica se este usuário específico já reclamou
    if notification.user is None:
        rewards_claimed = PublicNotificationRewardClaim.objects.filter(
            user=request.user, 
            notification=notification
        ).exists()
    else:
        rewards_claimed = notification.rewards_claimed
    has_unclaimed_rewards = has_rewards and not rewards_claimed and not rewards_expired
    
    data = {
        'type': notification.get_notification_type_display(),
        'message': notification.message,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'link': notification.link if notification.link else None,
        'has_rewards': has_rewards,
        'rewards_claimed': rewards_claimed,
        'rewards_expired': rewards_expired,
        'rewards_expires_at': notification.rewards_expires_at.strftime('%Y-%m-%d %H:%M:%S') if notification.rewards_expires_at else None,
        'has_unclaimed_rewards': has_unclaimed_rewards,
        'rewards': rewards_data,
    }

    return JsonResponse(data)


@conditional_otp_required
def all_notifications(request):
    user = request.user

    # Private notifications
    private_qs = Notification.objects.filter(user=user).prefetch_related('rewards').order_by('-created_at')
    if not (user.is_staff or user.is_superuser):
        private_qs = private_qs.exclude(notification_type='staff')

    # Public notifications
    public_qs = Notification.objects.filter(user=None).prefetch_related('rewards').order_by('-created_at')
    if not (user.is_staff or user.is_superuser):
        public_qs = public_qs.exclude(notification_type='staff')

    # Viewed public notifications
    viewed_public_ids = set(
        PublicNotificationView.objects.filter(user=user).values_list('notification_id', flat=True)
    )

    # Marcar instância como visualizada
    for n in public_qs:
        n.viewed = n.id in viewed_public_ids

    # Paginação
    private_paginator = Paginator(private_qs, 10)
    public_paginator = Paginator(public_qs, 10)

    private_page_number = request.GET.get('private_page')
    public_page_number = request.GET.get('public_page')

    private_notifications = private_paginator.get_page(private_page_number)
    public_notifications = public_paginator.get_page(public_page_number)

    # Calcular estatísticas
    total_notifications = private_qs.count() + public_qs.count()
    unread_private = private_qs.filter(viewed=False).count()
    unread_public = len([n for n in public_qs if n.id not in viewed_public_ids])
    unread_count = unread_private + unread_public
    
    # Contar notificações com prêmios
    notifications_with_rewards = (
        private_qs.filter(rewards__isnull=False).distinct().count() +
        public_qs.filter(rewards__isnull=False).distinct().count()
    )

    from utils.pagination_helper import prepare_pagination_context
    private_pagination = prepare_pagination_context(private_notifications)
    public_pagination = prepare_pagination_context(public_notifications)
    
    context = {
        'private_notifications': private_notifications,
        'public_notifications': public_notifications,
        'private_page_number': private_page_number,
        'public_page_number': public_page_number,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
        'notifications_with_rewards': notifications_with_rewards,
        'segment': 'index',
        'parent': 'notification',
        # Paginação privada
        'private_current_page': private_notifications.number,
        'private_total_pages': private_notifications.paginator.num_pages,
        'private_has_previous': private_notifications.has_previous(),
        'private_has_next': private_notifications.has_next(),
        'private_previous_page_number': private_notifications.previous_page_number() if private_notifications.has_previous() else None,
        'private_next_page_number': private_notifications.next_page_number() if private_notifications.has_next() else None,
        'private_page_range': private_pagination.get('page_range', []),
        'private_show_first': private_pagination.get('show_first', False),
        'private_show_last': private_pagination.get('show_last', False),
        'private_show_first_ellipsis': private_pagination.get('show_first_ellipsis', False),
        'private_show_last_ellipsis': private_pagination.get('show_last_ellipsis', False),
        # Paginação pública
        'public_current_page': public_notifications.number,
        'public_total_pages': public_notifications.paginator.num_pages,
        'public_has_previous': public_notifications.has_previous(),
        'public_has_next': public_notifications.has_next(),
        'public_previous_page_number': public_notifications.previous_page_number() if public_notifications.has_previous() else None,
        'public_next_page_number': public_notifications.next_page_number() if public_notifications.has_next() else None,
        'public_page_range': public_pagination.get('page_range', []),
        'public_show_first': public_pagination.get('show_first', False),
        'public_show_last': public_pagination.get('show_last', False),
        'public_show_first_ellipsis': public_pagination.get('show_first_ellipsis', False),
        'public_show_last_ellipsis': public_pagination.get('show_last_ellipsis', False),
    }
    return render(request, 'pages/notifications.html', context)


@conditional_otp_required
def confirm_notification_view(request, pk):
    notification = get_object_or_404(Notification, pk=pk)

    if notification.user == request.user:
        notification.viewed = True
        notification.save()
    elif notification.user is None:
        # Verifica se existe uma marcação de visualização para notificação pública
        public_notification_view, created = PublicNotificationView.objects.get_or_create(user=request.user, notification=notification)
        if created:
            public_notification_view.viewed = True
            public_notification_view.save()

    return JsonResponse({'status': 'success'})


@conditional_otp_required
def claim_rewards(request, pk):
    """Reclama os prêmios de uma notificação"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    notification = get_object_or_404(Notification, pk=pk)

    # Verifica permissão básica (notificações privadas)
    if notification.user and notification.user != request.user:
        return JsonResponse({'error': 'Você não tem permissão para reclamar prêmios desta notificação.'}, status=403)

    # Reclama os prêmios (a função claim_notification_rewards faz todas as validações)
    success, error_message = claim_notification_rewards(notification, request.user, request)
    
    if success:
        has_fichas = notification.rewards.filter(fichas_amount__gt=0).exists()
        rewards_count = notification.rewards.count()
        log_action(
            logger, "notification_claim_rewards", "sucesso",
            username=request.user.username,
            notification_id=notification.pk,
            notification_type=notification.notification_type,
            rewards_count=rewards_count,
            has_fichas=has_fichas,
        )
        message = 'Prêmios reclamados com sucesso!'
        if has_fichas:
            message += ' Verifique sua bag e suas fichas.'
        else:
            message += ' Verifique sua bag.'

        return JsonResponse({
            'status': 'success',
            'message': message
        })
    else:
        # Retorna a mensagem de erro específica
        error_msg = error_message or 'Erro ao reclamar prêmios.'
        return JsonResponse({'error': error_msg}, status=400)


@csrf_exempt
@login_required
def save_subscription(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    try:
        data = json.loads(request.body)
        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        auth = keys.get('auth')
        p256dh = keys.get('p256dh')
        if not (endpoint and auth and p256dh):
            return JsonResponse({'error': 'Dados incompletos'}, status=400)
        if endpoint and ('notify.windows.com' in endpoint or endpoint.startswith('https://wns2-')):
            return JsonResponse({'error': 'Push notifications não são suportadas neste navegador. Use Chrome, Firefox ou Edge Chromium.'}, status=400)
        # Remove subscriptions antigas do mesmo endpoint
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        PushSubscription.objects.create(
            user=request.user,
            endpoint=endpoint,
            auth=auth,
            p256dh=p256dh
        )
        return JsonResponse({'ok': True})
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        return JsonResponse({'error': str(e), 'traceback': tb, 'body': request.body.decode('utf-8', errors='replace')}, status=500)


@staff_member_required
def send_push_view(request):
    # Estatísticas para exibir na página
    subscribed_users_count = PushSubscription.objects.values('user').distinct().count()
    total_sent = PushNotificationLog.objects.aggregate(total=models.Sum('successful_sends'))['total'] or 0
    
    # Última notificação enviada
    last_push = PushNotificationLog.objects.first()
    last_sent = last_push.created_at.strftime('%d/%m/%Y %H:%M') if last_push else "Nunca"
    
    if request.method == 'POST':
        message = request.POST.get('message', '').strip()
        total = 0
        errors = []
        logger = logging.getLogger(__name__)
        
        if message:
            # Conta total de inscritos antes do envio
            total_subscribers = PushSubscription.objects.count()
            # Lista fixa para poder remover inscrições inválidas durante o loop
            subscriptions = list(PushSubscription.objects.all())

            for sub in subscriptions:
                subscription_info = {
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": getattr(sub, 'p256dh', ''),
                        "auth": sub.auth,
                    }
                }
                try:
                    webpush(
                        subscription_info=subscription_info,
                        data=json.dumps({"title": "PDL", "body": message, "url": "/"}),
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims={"sub": "mailto:seu@email.com"}
                    )
                    total += 1
                except WebPushException as ex:
                    logger.error(f"Erro ao enviar push para {sub.user}: {repr(ex)}")
                    errors.append(sub.user)
                    # 410 Gone / 400 Bad Request = inscrição expirada ou inválida; remove para não tentar de novo
                    if "410" in str(ex) or "400" in str(ex):
                        sub.delete()
                        logger.info(f"Inscrição push inválida removida para {sub.user} (endpoint expirado).")
            
            # Registra o log da notificação push
            PushNotificationLog.objects.create(
                message=message,
                sent_by=request.user,
                total_subscribers=total_subscribers,
                successful_sends=total,
                failed_sends=len(errors)
            )
            
            if total:
                messages.success(request, f"Notificações enviadas para {total} inscritos!")
            if errors:
                messages.error(request, f"Falha ao enviar notificações para {len(errors)} usuários. Consulte os logs para detalhes.")
        else:
            messages.error(request, "Mensagem não pode ser vazia.")
        return redirect('notification:send_push')
    
    context = {
        'subscribed_users_count': subscribed_users_count,
        'total_sent': total_sent,
        'last_sent': last_sent,
    }
    return render(request, 'notification/send_push.html', context)
