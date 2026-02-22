from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel
from apps.main.home.models import User

class ClanProfile(BaseModel):
    """
    Extensão Web para os Clans do Lineage 2.
    A associação com o jogo é feita pelo clan_id.
    """
    clan_id = models.PositiveIntegerField(unique=True, verbose_name=_("ID do Clã"))
    recruiting = models.BooleanField(default=False, verbose_name=_("Recrutando?"))
    min_level = models.PositiveIntegerField(default=1, verbose_name=_("Nível Mínimo"))
    required_classes = models.CharField(max_length=255, blank=True, verbose_name=_("Classes Exigidas"), help_text=_("Deixe em branco se aceitar qualquer classe"))
    motd = models.TextField(blank=True, verbose_name=_("Mensagem do Dia / Apresentação"))
    playtime_requirements = models.CharField(max_length=255, blank=True, verbose_name=_("Requisitos de Tempo de Jogo"))
    language = models.CharField(max_length=50, blank=True, default="Qualquer", verbose_name=_("Foco de Idioma / Região"))
    focus = models.CharField(
        max_length=20,
        choices=[
            ('PVP', _('Focado em PvP')),
            ('PVE', _('PvE / Farm')),
            ('MIXED', _('PvX (Misto)')),
            ('CASUAL', _('Casual / Social'))
        ],
        default='MIXED',
        verbose_name=_("Foco do Clã")
    )
    crest_image = models.ImageField(upload_to='clans/crests/', null=True, blank=True, verbose_name=_("Brasão Web Personalizado"))
    banner_image = models.ImageField(upload_to='clans/banners/', null=True, blank=True, verbose_name=_("Banner Web do Clã"))

    def __str__(self):
        return f"Perfil Web do Clã ID {self.clan_id}"

    class Meta:
        verbose_name = _("Perfil Web do Clã")
        verbose_name_plural = _("Perfis Web de Clãs")

class RecruitmentApplication(BaseModel):
    """
    Representa o "Currículo" que um jogador envia para o clã.
    """
    STATUS_CHOICES = [
        ('PENDING', _('Pendente')),
        ('APPROVED', _('Aprovado (Aguardando Convite no Jogo)')),
        ('REJECTED', _('Rejeitado')),
        ('COMPLETED', _('Concluído (Entrou no Clã)')),
        ('ARCHIVED', _('Arquivado / Cancelado'))
    ]

    clan_profile = models.ForeignKey(ClanProfile, on_delete=models.CASCADE, related_name='applications', verbose_name=_("Clã"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clan_applications', verbose_name=_("Conta do Jogador"))
    char_id = models.PositiveIntegerField(verbose_name=_("ID do Personagem"))
    char_name = models.CharField(max_length=100, verbose_name=_("Nome do Personagem"))
    message = models.TextField(verbose_name=_("Mensagem de Inscrição / Motivação"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name=_("Status"))
    leader_feedback = models.TextField(blank=True, verbose_name=_("Feedback do Líder"))

    def __str__(self):
        return f"{self.char_name} -> Clã ID {self.clan_profile.clan_id} ({self.status})"

    class Meta:
        verbose_name = _("Inscrição de Recrutamento")
        verbose_name_plural = _("Inscrições de Recrutamento")
        unique_together = ('clan_profile', 'char_id') # prevent spam to same clan
