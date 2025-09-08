from apps.main.notification.models import Notification
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext as _


def send_notification(user=None, notification_type='user', message='', created_by=None, link=None):
    """
    Cria uma notificação segura.

    - Se `user` for None, será considerada uma notificação pública.
    - Notificações do tipo 'staff' só podem ser enviadas para usuários com is_staff ou is_superuser.
    - `created_by` é opcional e pode ser usado para validar permissões de quem está criando.
    - `link` é uma URL opcional que será incluída na notificação.
    """

    if notification_type == 'staff':
        if user:
            if not (user.is_staff or user.is_superuser):
                raise PermissionDenied(_("Notificações staff só podem ser enviadas para usuários staff ou superusuários."))
        else:
            # Notificação pública staff — só deve ser criada se quem envia tem permissão
            if created_by and not (created_by.is_staff or created_by.is_superuser):
                raise PermissionDenied(_("Você não tem permissão para criar notificações públicas staff."))

    # Criação da notificação
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message,
        link=link
    )
