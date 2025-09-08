from django.db import models
from core.models import BaseModel
from django_ckeditor_5.fields import CKEditor5Field
from django.utils.translation import gettext_lazy as _


class FAQ(BaseModel):
    question = models.CharField(max_length=255, verbose_name=_("Pergunta"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordem"))
    is_public = models.BooleanField(default=True, verbose_name=_("Está público"))

    class Meta:
        ordering = ['order']
        verbose_name = _('Pergunta Frequente')
        verbose_name_plural = _('Perguntas Frequentes')

        permissions = [
            ("can_view_index", _("Pode visualizar o índice")),
        ]

    def __str__(self):
        pt_translation = self.translations.filter(language='pt').first()
        return pt_translation.question if pt_translation else f"FAQ {self.pk}"


class FAQTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('Inglês')),
        ('es', _('Espanhol')),
    ]

    faq = models.ForeignKey(FAQ, on_delete=models.CASCADE, related_name='translations', verbose_name=_("FAQ"))
    language = models.CharField(max_length=5, choices=LANGUAGES, verbose_name=_("Idioma"))
    question = models.CharField(max_length=255, verbose_name=_("Pergunta"))
    answer = CKEditor5Field(config_name='extends', verbose_name=_("Resposta"))

    class Meta:
        unique_together = ('faq', 'language')
        verbose_name = _('Tradução de FAQ')
        verbose_name_plural = _('Traduções de FAQ')

    def __str__(self):
        return f"{self.question} ({self.language})"
