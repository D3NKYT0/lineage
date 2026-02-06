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
# Eventos apenas para staff/admin (doações, loja, envios servidor)
EVENT_ADMIN_DOACOES_COMPRAS = "admin_doacoes_compras"
EVENT_ADMIN_USO_LOJAS = "admin_uso_lojas"
EVENT_ADMIN_ENVIOS_SERVIDOR = "admin_envios_servidor"

# Eventos que só são enviados para staff (quem pode habilitar no perfil)
STAFF_ONLY_EVENT_TYPES = frozenset({
    EVENT_ADMIN_DOACOES_COMPRAS,
    EVENT_ADMIN_USO_LOJAS,
    EVENT_ADMIN_ENVIOS_SERVIDOR,
})

# Lista para o formulário do perfil: (chave, label, staff_only)
PUSH_EVENT_CHOICES = [
    (EVENT_CONVITE_AMIZADE, _("Pedidos de amizade"), False),
    (EVENT_RESPOSTA_SOLICITACAO, _("Atualizações em solicitações (tickets)"), False),
    (EVENT_NOVO_EVENTO_SOLICITACAO, _("Novos eventos em solicitações"), False),
    (EVENT_LEILAO_VENDIDO, _("Leilão vendido (meus leilões)"), False),
    (EVENT_LEILAO_GANHO, _("Leilão ganho"), False),
    (EVENT_MARKETPLACE_VENDIDO, _("Personagem vendido no marketplace"), False),
    (EVENT_MARKETPLACE_COMPRA, _("Compra de personagem no marketplace"), False),
    (EVENT_ADMIN_DOACOES_COMPRAS, _("Doações / compras na carteira (admin)"), True),
    (EVENT_ADMIN_USO_LOJAS, _("Uso da loja (compras por jogadores) (admin)"), True),
    (EVENT_ADMIN_ENVIOS_SERVIDOR, _("Envios para o servidor (admin)"), True),
]

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
    EVENT_ADMIN_DOACOES_COMPRAS: (
        _("Nova doação/compra na carteira"),
        _("%(username)s realizou uma compra/doação de R$ %(valor)s."),
    ),
    EVENT_ADMIN_USO_LOJAS: (
        _("Compra na loja"),
        _("%(username)s realizou uma compra na loja: R$ %(valor)s."),
    ),
    EVENT_ADMIN_ENVIOS_SERVIDOR: (
        _("Envio para o servidor"),
        _("%(username)s enviou R$ %(valor)s para o personagem %(personagem)s."),
    ),
}


def user_wants_push(user, event_type):
    """
    Verifica se o usuário quer receber push para este tipo de evento.
    - Eventos staff_only: só aplicável se user for staff/superuser; senão retorna False.
    - Chave ausente em push_preferences = True (receber). Valor False = não receber.
    """
    if not user:
        return False
    if event_type in STAFF_ONLY_EVENT_TYPES:
        if not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
            return False
    try:
        perfil = getattr(user, "perfilgamer", None)
        if perfil is None:
            from apps.main.home.models import PerfilGamer
            perfil = PerfilGamer.objects.filter(user=user).first()
        prefs = getattr(perfil, "push_preferences", None) or {}
        return prefs.get(event_type, True)  # default True
    except Exception:
        return True  # em caso de erro, envia


def get_push_choices_for_user(user):
    """Retorna lista de (chave, label, staff_only) para exibir no perfil (staff vê opções admin)."""
    is_staff = getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)
    return [(key, label, staff_only) for key, label, staff_only in PUSH_EVENT_CHOICES if not staff_only or is_staff]


def send_push_to_staff_for_event(event_type, title=None, body=None, url=None, async_send=True, **template_context):
    """
    Envia push para todos os staff que tenham preferência habilitada para este evento.
    event_type deve ser um dos EVENT_ADMIN_*.
    """
    from django.db.models import Q
    from apps.main.home.models import User
    staff_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).distinct()
    for staff in staff_users:
        if user_wants_push(staff, event_type):
            send_push_for_event(staff, event_type, title=title, body=body, url=url, async_send=async_send, **template_context)


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
    Respeita as preferências do perfil (push_preferences). Use para eventos do painel.

    - user: usuário alvo (objeto User).
    - event_type: uma das constantes EVENT_* (ex: EVENT_CONVITE_AMIZADE).
    - title, body, url: opcionais; se não passados, usam o template do event_type.
    - template_context: kwargs para formatar body com %(key)s (ex: username=..., protocol=...).
    - async_send: se True, agenda envio via Celery; se False, envia de forma síncrona.
    """
    if not user:
        return
    if not user_wants_push(user, event_type):
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
    if async_send and not getattr(settings, "PUSH_ALWAYS_SYNC", False):
        try:
            from apps.main.notification.tasks import send_push_notification_async, execute_task_sync_or_async
            # Em DEBUG executa síncrono; em produção usa .delay() (ou síncrono se PUSH_ALWAYS_SYNC=True)
            execute_task_sync_or_async(
                send_push_notification_async,
                user.id,
                title=title,
                body=body,
                url=url,
            )
        except Exception as e:
            logger.warning("Falha ao agendar push por evento: %s", e)
            send_webpush_notification(user, title, body, url)
    elif async_send and getattr(settings, "PUSH_ALWAYS_SYNC", False):
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