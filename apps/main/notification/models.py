from django.db import models
from core.models import BaseModel
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from encrypted_fields.encrypted_fields import *
from encrypted_fields.encrypted_files import *
from utils.choices import *


class Notification(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Usuário"),
        help_text=_("Usuário relacionado à notificação (pode ser nulo para notificações públicas).")
    )
    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        verbose_name=_("Tipo de Notificação"),
        help_text=_("Tipo ou categoria da notificação.")
    )
    message = EncryptedCharField(
        max_length=255,
        verbose_name=_("Mensagem"),
        help_text=_("Mensagem da notificação (criptografada).")
    )
    viewed = models.BooleanField(
        default=False,
        verbose_name=_("Visualizada"),
        help_text=_("Indica se a notificação foi visualizada pelo usuário.")
    )
    link = models.URLField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name=_("Link da Notificação"),
        help_text=_("URL opcional para redirecionar ao clicar na notificação.")
    )

    class Meta:
        verbose_name = _("Notificação")
        verbose_name_plural = _("Notificações")

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.message[:50]}..."


class PublicNotificationView(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que visualizou a notificação pública.")
    )
    notification = models.ForeignKey(
        Notification,
        on_delete=models.CASCADE,
        verbose_name=_("Notificação"),
        help_text=_("Referência à notificação visualizada.")
    )
    viewed = models.BooleanField(
        default=False,
        verbose_name=_("Visualizada"),
        help_text=_("Indica se o usuário visualizou essa notificação pública.")
    )

    class Meta:
        verbose_name = _("Visualização de Notificação Pública")
        verbose_name_plural = _("Visualizações de Notificações Públicas")


class PushSubscription(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('Usuário'),
        help_text=_('Usuário dono do subscription.')
    )
    endpoint = models.URLField(max_length=500)
    auth = models.CharField(max_length=255)
    p256dh = models.CharField(max_length=255)

    class Meta:
        verbose_name = _('Push Subscription')
        verbose_name_plural = _('Push Subscriptions')

    def __str__(self):
        return f"{self.user} - {self.endpoint[:30]}..."


class PushNotificationLog(BaseModel):
    message = models.TextField(
        verbose_name=_("Mensagem"),
        help_text=_("Mensagem enviada via push.")
    )
    sent_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Enviado por"),
        help_text=_("Usuário que enviou a notificação push.")
    )
    total_subscribers = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Total de Inscritos"),
        help_text=_("Número total de usuários inscritos no momento do envio.")
    )
    successful_sends = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Enviados com Sucesso"),
        help_text=_("Número de notificações enviadas com sucesso.")
    )
    failed_sends = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Falhas no Envio"),
        help_text=_("Número de notificações que falharam ao enviar.")
    )

    class Meta:
        verbose_name = _("Log de Notificação Push")
        verbose_name_plural = _("Logs de Notificações Push")
        ordering = ['-created_at']

    def __str__(self):
        return f"Push enviado por {self.sent_by} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
