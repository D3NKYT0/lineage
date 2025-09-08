from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
from pywebpush import webpush, WebPushException
from django.conf import settings
from apps.main.notification.models import PushSubscription

def send_push_notification(user, message, link=None, notification_id=None):
    """
    Envia uma notificação push em tempo real via Channels para o usuário informado.
    Não cria notificação no banco, apenas envia via WebSocket.
    """
    if not user:
        return
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user.id}",
        {
            "type": "send_notification",
            "message": message,
            "link": link,
            "notification_id": notification_id,
        }
    )

def send_webpush_notification(user, title, body, url=None):
    """
    Envia push notification via Web Push API para todos os subscriptions do usuário.
    """
    payload = {
        "title": title,
        "body": body,
        "url": url or "/"
    }
    vapid_private_key = settings.VAPID_PRIVATE_KEY
    vapid_claims = {
        "sub": "mailto:contato@seudominio.com"  # Altere para seu email
    }
    for sub in PushSubscription.objects.filter(user=user):
        subscription_info = {
            "endpoint": sub.endpoint,
            "keys": {
                "auth": sub.auth,
                "p256dh": sub.p256dh
            }
        }
        try:
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims
            )
        except WebPushException as ex:
            # Se falhar, pode remover o subscription inválido
            sub.delete() 