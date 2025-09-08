from django.db import models
from django.utils.translation import gettext_lazy as _
from utils.protocol import create_protocol
from apps.main.home.models import User
from core.models import BaseModel
from .choices import STATUS_CHOICES, CATEGORY_CHOICES, PRIORITY_CHOICES


class Solicitation(BaseModel):
    protocol = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        verbose_name=_("Protocolo"),
        help_text=_("Código de identificação único da solicitação.")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Título"),
        help_text=_("Título da solicitação.")
    )
    description = models.TextField(
        verbose_name=_("Descrição"),
        help_text=_("Descrição detalhada da solicitação.")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open',
        verbose_name=_("Status"),
        help_text=_("Status atual da solicitação.")
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        verbose_name=_("Categoria"),
        help_text=_("Categoria da solicitação.")
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        verbose_name=_("Prioridade"),
        help_text=_("Prioridade da solicitação.")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='solicitations_user',
        blank=True,
        null=True,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que iniciou a solicitação.")
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='solicitations_assigned',
        blank=True,
        null=True,
        verbose_name=_("Atribuído para"),
        help_text=_("Usuário responsável por resolver a solicitação.")
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Resolvido em"),
        help_text=_("Data e hora em que a solicitação foi resolvida.")
    )
    closed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Fechado em"),
        help_text=_("Data e hora em que a solicitação foi fechada.")
    )

    def add_participant(self, user):
        """Adiciona um participante à proposta."""
        SolicitationParticipant.objects.get_or_create(solicitation=self, user=user)

    def is_participant(self, user):
        """Verifica se o usuário é um dos participantes da proposta."""
        return SolicitationParticipant.objects.filter(solicitation=self, user=user).exists()

    def can_be_resolved(self):
        """Verifica se a solicitação pode ser resolvida."""
        return self.status in ['open', 'pending', 'in_progress', 'waiting_user', 'waiting_third_party']

    def can_be_closed(self):
        """Verifica se a solicitação pode ser fechada."""
        return self.status in ['resolved', 'open', 'pending', 'in_progress']

    def get_display_protocol(self):
        """Retorna o protocolo formatado para exibição."""
        if self.protocol and self.protocol.strip():
            return self.protocol
        return None

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        # Garante que sempre há um protocolo
        if not self.protocol or self.protocol.strip() == '':
            self.protocol = create_protocol()
        
        # Atualiza timestamps baseado no status
        if self.status == 'resolved' and not self.resolved_at:
            from django.utils import timezone
            self.resolved_at = timezone.now()
        elif self.status == 'closed' and not self.closed_at:
            from django.utils import timezone
            self.closed_at = timezone.now()
        
        super().save(*args, **kwargs)

        if is_new and self.user:
            SolicitationParticipant.objects.get_or_create(solicitation=self, user=self.user)

        # Cria histórico apenas para novas solicitações
        if is_new:
            SolicitationHistory.objects.create(solicitation=self, action=_('Solicitação criada.'))

    def __str__(self):
        return f"{_('Solicitação')} {self.protocol} - {self.title} ({self.status})"

    class Meta:
        verbose_name = _("Solicitação")
        verbose_name_plural = _("Solicitações")
        ordering = ['-created_at']


class SolicitationParticipant(BaseModel):
    solicitation = models.ForeignKey(
        Solicitation,
        on_delete=models.CASCADE,
        related_name='solicitation_participants',
        verbose_name=_("Solicitação")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='solicitations_users',
        verbose_name=_("Usuário")
    )

    def __str__(self):
        return f'{self.user.username} - {self.solicitation.protocol}'

    class Meta:
        verbose_name = _("Participante da Solicitação")
        verbose_name_plural = _("Participantes da Solicitação")
        unique_together = ('solicitation', 'user')


class SolicitationHistory(BaseModel):
    solicitation = models.ForeignKey(
        Solicitation,
        on_delete=models.CASCADE,
        related_name='solicitation_history',
        verbose_name=_("Solicitação")
    )
    action = models.CharField(
        max_length=255,
        verbose_name=_("Ação"),
        help_text=_("Descrição da ação realizada.")
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data e Hora"),
        help_text=_("Momento em que a ação foi registrada.")
    )
    image = models.ImageField(
        upload_to='solicitation_history_images/',
        null=True,
        blank=True,
        verbose_name=_("Imagem"),
        help_text=_("Imagem opcional associada à ação.")
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Usuário"),
        help_text=_("Usuário que realizou a ação.")
    )

    def __str__(self):
        return f"{_('Histórico da Solicitação')} {self.solicitation.protocol} - {self.timestamp}"

    class Meta:
        verbose_name = _("Histórico da Solicitação")
        verbose_name_plural = _("Históricos da Solicitação")
