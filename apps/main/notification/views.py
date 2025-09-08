from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.db import models
from apps.main.home.decorator import conditional_otp_required
from .models import Notification, PublicNotificationView, PushSubscription, PushNotificationLog
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from pywebpush import webpush, WebPushException
import logging


@conditional_otp_required
def get_notifications(request):
    # Notificações privadas do usuário (exclui staff se user não for staff/superuser)
    user_notifications = Notification.objects.filter(
        user=request.user,
        viewed=False
    ).exclude(
        notification_type='staff'
    ).order_by('-created_at')

    if request.user.is_staff or request.user.is_superuser:
        # Se for staff/superuser, incluir também notificações staff pra ele
        staff_notifications = Notification.objects.filter(
            user=request.user,
            notification_type='staff',
            viewed=False
        ).order_by('-created_at')
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

    notifications_list = []

    # Notificações privadas
    for notification in user_notifications:
        notifications_list.append({
            'id': notification.id,
            'message': notification.message,
            'type': notification.notification_type,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'viewed': notification.viewed,
            'detail_url': reverse('notification:notification_detail', args=[notification.id])
        })

    # Notificações públicas
    for notification in public_notifications:
        if notification.id not in public_notifications_viewed_ids:
            notifications_list.append({
                'id': notification.id,
                'message': notification.message,
                'type': notification.notification_type,
                'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'viewed': False,
                'detail_url': reverse('notification:notification_detail', args=[notification.id])
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

    data = {
        'type': notification.get_notification_type_display(),
        'message': notification.message,
        'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'link': notification.link if notification.link else None,
    }

    return JsonResponse(data)


@conditional_otp_required
def all_notifications(request):
    user = request.user

    # Private notifications
    private_qs = Notification.objects.filter(user=user).order_by('-created_at')
    if not (user.is_staff or user.is_superuser):
        private_qs = private_qs.exclude(notification_type='staff')

    # Public notifications
    public_qs = Notification.objects.filter(user=None).order_by('-created_at')
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

    context = {
        'private_notifications': private_notifications,
        'public_notifications': public_notifications,
        'segment': 'index',
        'parent': 'notification',
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
            
            for sub in PushSubscription.objects.all():
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
                        data=json.dumps({"body": message}),
                        vapid_private_key=settings.VAPID_PRIVATE_KEY,
                        vapid_claims={"sub": "mailto:seu@email.com"}
                    )
                    total += 1
                except WebPushException as ex:
                    logger.error(f"Erro ao enviar push para {sub.user}: {repr(ex)}")
                    errors.append(sub.user)
            
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
