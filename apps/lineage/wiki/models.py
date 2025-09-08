from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from core.models import BaseModel
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings


class WikiPage(BaseModel):
    """Modelo principal para páginas do Wiki"""
    CONTENT_TYPES = [
        ('index', _('Página Inicial')),
        ('about', _('Sobre o Servidor')),
        ('rules', _('Regras do Servidor')),
        ('commands', _('Comandos do Jogo')),
        ('classes', _('Classes de Personagem')),
        ('races', _('Raças de Personagem')),
        ('noblesse', _('Sistema Noblesse')),
        ('subclass', _('Sistema Subclass')),
        ('hero', _('Sistema Hero')),
        ('clan', _('Sistema Clan')),
        ('siege', _('Sistema Siege')),
        ('olympiad', _('Sistema Olympiad')),
        ('castle', _('Sistema Castle')),
        ('fortress', _('Sistema Fortress')),
        ('territory', _('Sistema Territory')),
        ('events', _('Eventos do Servidor')),
        ('updates', _('Atualizações')),
        ('features', _('Funcionalidades')),
        ('rates', _('Taxas do Servidor')),
        ('raids', _('Raids e Bosses')),
        ('assistance', _('Assistência e Suporte')),
        ('guide', _('Guias e Tutoriais')),
        ('faq', _('Perguntas Frequentes')),
        ('other', _('Outros')),
    ]

    content_type = models.CharField(
        max_length=50,
        choices=CONTENT_TYPES,
        verbose_name=_("Tipo de Conteúdo"),
        help_text=_("Tipo de conteúdo desta página")
    )
    slug = models.SlugField(
        _('Slug'),
        unique=True,
        blank=True,
        help_text=_("URL amigável da página (gerado automaticamente)")
    )
    order = models.IntegerField(
        _('Ordem'),
        default=0,
        help_text=_("Ordem de exibição")
    )
    is_active = models.BooleanField(
        _('Ativo'),
        default=True,
        help_text=_("Se a página está visível")
    )
    is_menu_item = models.BooleanField(
        _('Item do Menu'),
        default=False,
        help_text=_("Se deve aparecer no menu de navegação")
    )
    icon = models.CharField(
        _('Ícone'),
        max_length=50,
        blank=True,
        help_text=_("Nome do ícone (ex: fas fa-home, bi bi-gear)")
    )
    parent_page = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Página Pai"),
        help_text=_("Página pai para criar hierarquia")
    )
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Página do Wiki')
        verbose_name_plural = _('Páginas do Wiki')
        ordering = ['order', 'content_type', 'translations__title']

    def save(self, *args, **kwargs):
        if not self.slug:
            pt_translation = self.translations.filter(language='pt').first()
            if pt_translation:
                self.slug = slugify(pt_translation.title)
        super(WikiPage, self).save(*args, **kwargs)

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        if pt_translation:
            return f"{self.get_content_type_display()}: {pt_translation.title}"
        return f"{self.get_content_type_display()} (ID: {self.pk})"


class WikiPageTranslation(BaseModel):
    """Traduções das páginas do Wiki"""
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('Inglês')),
        ('es', _('Espanhol')),
    ]

    page = models.ForeignKey(
        WikiPage,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Página")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Idioma")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Título"),
        help_text=_("Título da página")
    )
    subtitle = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Subtítulo"),
        help_text=_("Subtítulo opcional")
    )
    content = CKEditor5Field(
        verbose_name=_("Conteúdo"),
        config_name='extends',
        help_text=_("Conteúdo principal da página")
    )
    summary = models.TextField(
        blank=True,
        verbose_name=_("Resumo"),
        help_text=_("Resumo para exibição em listas")
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name=_("Meta Descrição"),
        help_text=_("Descrição para SEO")
    )

    class Meta:
        unique_together = ('page', 'language')
        verbose_name = _("Tradução da Página")
        verbose_name_plural = _("Traduções das Páginas")

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"


class WikiUpdate(BaseModel):
    """Modelo para atualizações do servidor"""
    version = models.CharField(
        _('Versão'),
        max_length=50,
        help_text=_("Número da versão (ex: 1.0.0)")
    )
    release_date = models.DateField(
        _('Data de Lançamento'),
        help_text=_("Data em que a versão foi lançada")
    )
    is_active = models.BooleanField(
        _('Ativo'),
        default=True,
        help_text=_("Se a atualização está visível")
    )
    is_major = models.BooleanField(
        _('Atualização Principal'),
        default=False,
        help_text=_("Se é uma atualização importante")
    )
    created_at = models.DateTimeField(_('Criado em'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Atualizado em'), auto_now=True)

    class Meta:
        verbose_name = _('Atualização do Servidor')
        verbose_name_plural = _('Atualizações do Servidor')
        ordering = ['-release_date', '-version']

    def __str__(self):
        return f"v{self.version} - {self.release_date}"


class WikiUpdateTranslation(BaseModel):
    """Traduções das atualizações"""
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('Inglês')),
        ('es', _('Espanhol')),
    ]

    update = models.ForeignKey(
        WikiUpdate,
        on_delete=models.CASCADE,
        related_name='translations',
        verbose_name=_("Atualização")
    )
    language = models.CharField(
        max_length=5,
        choices=LANGUAGES,
        verbose_name=_("Idioma")
    )
    title = models.CharField(
        max_length=200,
        verbose_name=_("Título"),
        help_text=_("Título da atualização")
    )
    content = CKEditor5Field(
        verbose_name=_("Conteúdo"),
        config_name='extends',
        help_text=_("Detalhes da atualização")
    )
    changelog = CKEditor5Field(
        verbose_name=_("Changelog"),
        config_name='extends',
        blank=True,
        help_text=_("Lista de mudanças")
    )

    class Meta:
        unique_together = ('update', 'language')
        verbose_name = _("Tradução da Atualização")
        verbose_name_plural = _("Traduções das Atualizações")

    def __str__(self):
        return f"{self.title} ({self.get_language_display()})"
