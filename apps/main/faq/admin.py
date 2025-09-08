from django import forms
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import FAQ, FAQTranslation
from core.admin import BaseModelAdmin


class FAQAdminForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = '__all__'
        widgets = {
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Pergunta')}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': _('Ordem')}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class FAQTranslationInline(admin.TabularInline):
    model = FAQTranslation
    fields = ('language', 'question', 'answer')
    verbose_name = _('Tradução')
    verbose_name_plural = _('Traduções')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['language'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width: 120px;'
        })
        formset.form.base_fields['question'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Pergunta'),
            'style': 'width: 100%;'
        })
        formset.form.base_fields['answer'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Resposta'),
            'rows': 3,
            'style': 'width: 100%;'
        })
        return formset


@admin.register(FAQ)
class FAQAdmin(BaseModelAdmin):
    form = FAQAdminForm
    list_display = ('get_question', 'order', 'is_public', 'get_languages', 'created_at')
    ordering = ('order', 'created_at')
    list_filter = ('is_public', 'created_at', 'translations__language')
    search_fields = ('translations__question', 'translations__answer')
    list_editable = ('order', 'is_public')
    inlines = [FAQTranslationInline]
    
    fieldsets = (
        (_('Configurações Básicas'), {
            'fields': ('order', 'is_public'),
            'description': _('Configure a ordem de exibição e visibilidade da FAQ')
        }),
    )
    
    actions = ['make_public', 'make_private', 'reorder_faqs']

    def get_question(self, obj):
        """Retorna a pergunta em português ou a primeira disponível"""
        pt_translation = obj.translations.filter(language='pt').first()
        if pt_translation:
            return pt_translation.question
        first_translation = obj.translations.first()
        if first_translation:
            return format_html(
                '<span style="color: #666;">[{}] {}</span>',
                first_translation.language.upper(),
                first_translation.question
            )
        return _('Sem tradução')
    get_question.short_description = _('Pergunta')
    get_question.admin_order_field = 'translations__question'

    def get_languages(self, obj):
        """Mostra os idiomas disponíveis"""
        languages = obj.translations.values_list('language', flat=True)
        if languages:
            badges = []
            for lang in languages:
                color = '#28a745' if lang == 'pt' else '#17a2b8'
                badges.append(
                    format_html(
                        '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 10px; margin: 1px;">{}</span>',
                        color, lang.upper()
                    )
                )
            return format_html(' '.join(badges))
        return format_html(
            '<span style="color: #dc3545; font-size: 11px;">{}</span>',
            _('Sem traduções')
        )
    get_languages.short_description = _('Idiomas')

    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, _('{} FAQs foram tornadas públicas.').format(updated))
    make_public.short_description = _('Tornar públicas')

    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, _('{} FAQs foram tornadas privadas.').format(updated))
    make_private.short_description = _('Tornar privadas')

    def reorder_faqs(self, request, queryset):
        """Reordena as FAQs baseado na ordem atual"""
        for i, faq in enumerate(queryset.order_by('order'), 1):
            faq.order = i
            faq.save()
        self.message_user(request, _('Ordem das FAQs foi reorganizada.'))
    reorder_faqs.short_description = _('Reorganizar ordem')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.faq = form.instance
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('translations')

    class Media:
        css = {
            'all': ('admin/css/faq_admin.css',)
        }
        js = ('admin/js/faq_admin.js',)
