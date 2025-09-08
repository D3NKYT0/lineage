from django.db import models
from core.models import BaseModel
from django.utils.translation import gettext_lazy as _

class DownloadCategory(BaseModel):
    name = models.CharField(max_length=100, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    order = models.IntegerField(default=0, verbose_name=_("Ordem"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Categoria de Download")
        verbose_name_plural = _("Categorias de Download")
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

class DownloadLink(BaseModel):
    DOWNLOAD_TYPES = [
        ('client', _('Cliente')),
        ('patch', _('Patch')),
        ('guide', _('Guia')),
        ('other', _('Outro')),
    ]

    HOSTING_TYPES = [
        ('mega', 'MEGA'),
        ('mediafire', 'MediaFire'),
        ('google_drive', 'Google Drive'),
        ('dropbox', 'Dropbox'),
        ('direct', _('Link Direto')),
        ('other', _('Outro')),
    ]

    category = models.ForeignKey(
        DownloadCategory,
        on_delete=models.CASCADE,
        related_name='downloads',
        verbose_name=_("Categoria")
    )
    name = models.CharField(max_length=200, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    download_type = models.CharField(
        max_length=20,
        choices=DOWNLOAD_TYPES,
        verbose_name=_("Tipo de Download")
    )
    hosting_type = models.CharField(
        max_length=20,
        choices=HOSTING_TYPES,
        verbose_name=_("Tipo de Hospedagem")
    )
    url = models.URLField(verbose_name=_("URL"))
    file_size = models.CharField(max_length=50, blank=True, verbose_name=_("Tamanho do Arquivo"))
    version = models.CharField(max_length=50, blank=True, verbose_name=_("Versão"))
    is_active = models.BooleanField(default=True, verbose_name=_("Ativo"))
    order = models.IntegerField(default=0, verbose_name=_("Ordem"))
    download_count = models.IntegerField(default=0, verbose_name=_("Contagem de Downloads"))

    class Meta:
        verbose_name = _("Link de Download")
        verbose_name_plural = _("Links de Download")
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_download_type_display()})"

    def increment_download_count(self):
        self.download_count += 1
        self.save(update_fields=['download_count']) 