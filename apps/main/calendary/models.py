from django.db import models
from django.contrib.auth import get_user_model
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


User = get_user_model()


class Event(BaseModel):
    title = models.CharField(_('Título'), max_length=200)
    start_date = models.DateTimeField(_('Data de início'))
    end_date = models.DateTimeField(_('Data de término'))
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('Usuário'), null=True, blank=True)
    className = models.CharField(
        _('Cor'),
        max_length=20,
        default='bg-red',
        choices=[
            ('bg-red', _('Vermelho')),
            ('bg-orange', _('Laranja')),
            ('bg-green', _('Verde')),
            ('bg-blue', _('Azul')),
            ('bg-purple', _('Roxo')),
            ('bg-info', _('Info')),
            ('bg-yellow', _('Amarelo')),
            ('bg-secondary', _('Cinza'))
        ]
    )

    def clean(self):
        super().clean()
        if self.end_date < self.start_date:
            raise ValidationError(_('A data de término não pode ser anterior à data de início.'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Evento')
        verbose_name_plural = _('Eventos')

    def __str__(self):
        return self.title
