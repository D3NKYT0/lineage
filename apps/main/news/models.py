from django.db import models
from core.models import BaseModel
from apps.main.home.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field


class News(BaseModel):
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("Endereço amigável da notícia, gerado automaticamente a partir do título.")
    )
    image = models.ImageField(
        upload_to='news',
        blank=True,
        null=True,
        verbose_name=_("Imagem"),
        help_text=_("Imagem de capa da notícia (opcional).")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_("Autor"),
        help_text=_("Usuário responsável pela publicação.")
    )
    pub_date = models.DateTimeField(
        _("Data de Publicação"),
        default=timezone.now,
        help_text=_("Data e hora em que a notícia foi ou será publicada.")
    )
    is_published = models.BooleanField(
        default=False,
        verbose_name=_("Publicado"),
        help_text=_("Indica se a notícia está visível ao público.")
    )
    is_private = models.BooleanField(
        default=False,
        verbose_name=_("Privado"),
        help_text=_("Se marcado, a notícia será visível apenas para usuários autorizados.")
    )

    class Meta:
        verbose_name = _("Notícia")
        verbose_name_plural = _("Notícias")
        permissions = [
            ("can_view_index", _("Pode visualizar a lista de notícias")),
            ("can_view_detail", _("Pode visualizar o detalhe da notícia")),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            pt_translation = self.translations.filter(language='pt').first()
            if pt_translation:
                self.slug = slugify(pt_translation.title)
        super(News, self).save(*args, **kwargs)

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.title if pt_translation else f"{_('Notícia')} {self.pk}"


class NewsTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('Inglês')),
        ('es', _('Espanhol')),
    ]

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Notícia")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Idioma"),
        help_text=_("Idioma da tradução.")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Título"),
        help_text=_("Título da notícia neste idioma.")
    )
    content = CKEditor5Field(
        verbose_name=_("Conteúdo"),
        config_name='extends'
    )
    summary = models.TextField(
        blank=True,
        verbose_name=_("Resumo"),
        help_text=_("Resumo opcional para exibição em listas.")
    )

    class Meta:
        unique_together = ('news', 'language')
        verbose_name = _("Tradução de Notícia")
        verbose_name_plural = _("Traduções de Notícias")

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"
