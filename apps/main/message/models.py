from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.utils.translation import gettext_lazy as _


class Friendship(BaseModel):
    user = models.ForeignKey(
        User,
        related_name='friends',
        on_delete=models.CASCADE,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que iniciou a amizade.")
    )
    friend = models.ForeignKey(
        User,
        related_name='friend_of',
        on_delete=models.CASCADE,
        verbose_name=_("Amigo"),
        help_text=_("Usuário que é amigo do primeiro usuário.")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data de Criação"),
        help_text=_("Data e hora em que a amizade foi criada.")
    )
    accepted = models.BooleanField(
        default=False,
        verbose_name=_("Aceita"),
        help_text=_("Indica se a amizade foi aceita.")
    )

    class Meta:
        unique_together = ('user', 'friend')
        verbose_name = _("Amizade")
        verbose_name_plural = _("Amizades")

    def __str__(self):
        return f"{self.user.username} e {self.friend.username} - {'Aceita' if self.accepted else 'Pendente'}"


class Chat(BaseModel):
    user1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats_user1',
        verbose_name=_("Usuário 1"),
        help_text=_("Primeiro usuário no chat.")
    )
    user2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='chats_user2',
        verbose_name=_("Usuário 2"),
        help_text=_("Segundo usuário no chat.")
    )
    last_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Última Mensagem"),
        help_text=_("Conteúdo da última mensagem no chat.")
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Última Atualização"),
        help_text=_("Data e hora da última atualização do chat.")
    )

    class Meta:
        unique_together = ('user1', 'user2')
        verbose_name = _("Conversação")
        verbose_name_plural = _("Conversações")

    def __str__(self):
        return f"Chat entre {self.user1.username} e {self.user2.username}"


class Message(BaseModel):
    chat = models.ForeignKey(
        Chat,
        related_name='messages',
        on_delete=models.CASCADE,
        verbose_name=_("Chat"),
        help_text=_("Chat ao qual a mensagem pertence.")
    )
    sender = models.ForeignKey(
        User,
        related_name='sent_messages',
        on_delete=models.CASCADE,
        verbose_name=_("Remetente"),
        help_text=_("Usuário que enviou a mensagem.")
    )
    text = models.TextField(
        verbose_name=_("Texto"),
        help_text=_("Conteúdo da mensagem.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data e Hora"),
        help_text=_("Data e hora em que a mensagem foi enviada.")
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_("Lida"),
        help_text=_("Indica se a mensagem foi lida.")
    )

    class Meta:
        verbose_name = _("Histórico de Conversas")
        verbose_name_plural = _("Históricos de Conversas")

    def __str__(self):
        return f"Mensagem de {self.sender.username} às {self.timestamp}"

    @classmethod
    def mark_as_read(cls, chat_id, user):
        """
        Marca todas as mensagens de um chat como lidas para um determinado usuário,
        exceto as mensagens enviadas pelo próprio usuário.
        """
        cls.objects.filter(chat_id=chat_id, is_read=False).exclude(sender=user).update(is_read=True)
