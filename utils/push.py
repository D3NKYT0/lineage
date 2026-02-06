from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json
import logging
from pywebpush import webpush, WebPushException
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _
from apps.main.notification.models import PushSubscription

logger = logging.getLogger(__name__)

# Tipos de evento para push (uso em send_push_for_event)
EVENT_CONVITE_AMIZADE = "convite_amizade"
EVENT_RESPOSTA_SOLICITACAO = "resposta_solicitacao"
EVENT_NOVO_EVENTO_SOLICITACAO = "novo_evento_solicitacao"
EVENT_LEILAO_VENDIDO = "leilao_vendido"       # para o vendedor
EVENT_LEILAO_GANHO = "leilao_ganho"           # para o comprador
EVENT_MARKETPLACE_VENDIDO = "marketplace_vendido"   # para o vendedor
EVENT_MARKETPLACE_COMPRA = "marketplace_compra"     # para o comprador

# Templates padrão por tipo de evento: (title, body)
PUSH_EVENT_TEMPLATES = {
    EVENT_CONVITE_AMIZADE: (
        _("Pedido de amizade"),
        _("%(username)s enviou um pedido de amizade."),
    ),
    EVENT_RESPOSTA_SOLICITACAO: (
        _("Atualização na sua solicitação"),
        _("Sua solicitação %(protocol)s teve o status alterado."),
    ),
    EVENT_NOVO_EVENTO_SOLICITACAO: (
        _("Novo evento na sua solicitação"),
        _("Foi adicionado um evento à sua solicitação %(protocol)s."),
    ),
    EVENT_LEILAO_VENDIDO: (
        _("Leilão vendido"),
        _("Seu leilão do item %(item_name)s foi vendido."),
    ),
    EVENT_LEILAO_GANHO: (
        _("Você ganhou o leilão!"),
        _("Você ganhou o leilão do item %(item_name)s."),
    ),
    EVENT_MARKETPLACE_VENDIDO: (
        _("Personagem vendido"),
        _("Seu personagem %(char_name)s foi vendido no marketplace."),
    ),
    EVENT_MARKETPLACE_COMPRA: (
        _("Compra realizada"),
        _("Você comprou o personagem %(char_name)s no marketplace."),
    ),
}


def send_push_for_event(
    user,
    event_type,
    title=None,
    body=None,
    url=None,
    async_send=True,
    **template_context
):
    """
    Envia push notification por tipo de evento (como um "envio de email" para push).
    Use para eventos do painel: convite de amizade, resposta de solicitação, venda, etc.

    - user: usuário alvo (objeto User).
    - event_type: uma das constantes EVENT_* (ex: EVENT_CONVITE_AMIZADE).
    - title, body, url: opcionais; se não passados, usam o template do event_type.
    - template_context: kwargs para formatar body com %(key)s (ex: username=..., protocol=...).
    - async_send: se True, agenda envio via Celery; se False, envia de forma síncrona.
    """
    if not user:
        return
    template = PUSH_EVENT_TEMPLATES.get(event_type)
    if template:
        t_title, t_body = template
        if title is None:
            title = t_title
        if body is None:
            try:
                body = t_body % template_context
            except KeyError:
                body = t_body
    if not title:
        title = _("Notificação")
    if not body:
        body = _("Você tem uma nova notificação.")
    if async_send:
        try:
            from apps.main.notification.tasks import send_push_notification_async
            send_push_notification_async.delay(user.id, title, body, url)
        except Exception as e:
            logger.warning("Falha ao agendar push por evento: %s", e)
            send_webpush_notification(user, title, body, url)
    else:
        send_webpush_notification(user, title, body, url)


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