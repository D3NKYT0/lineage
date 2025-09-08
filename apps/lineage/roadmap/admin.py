from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Roadmap, RoadmapTranslation
from core.admin import BaseModelAdmin, BaseInlineAdmin


class RoadmapTranslationInline(BaseInlineAdmin):
    model = RoadmapTranslation
    fields = ('language', 'title', 'content', 'summary')
    verbose_name = _('Tradução')
    verbose_name_plural = _('Traduções')
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.base_fields['language'].widget.attrs.update({
            'class': 'form-control',
            'style': 'width: 150px;'
        })
        formset.form.base_fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Título'),
            'style': 'width: 100%;'
        })
        formset.form.base_fields['summary'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': _('Resumo'),
            'rows': 3,
            'style': 'width: 100%;'
        })
        return formset


@admin.register(Roadmap)
class RoadmapAdmin(BaseModelAdmin):
    list_display = ('get_title', 'status', 'is_published', 'is_private', 'author', 'pub_date', 'get_languages', 'created_at')
    list_filter = ('status', 'is_published', 'is_private', 'pub_date', 'created_at', 'author', 'translations__language')
    search_fields = ('translations__title', 'translations__content', 'translations__summary', 'author__username')
    autocomplete_fields = ['author']
    ordering = ('-pub_date', '-created_at')
    list_editable = ('status', 'is_published', 'is_private')
    inlines = [RoadmapTranslationInline]
    
    fieldsets = (
        (_('Configurações de Publicação'), {
            'fields': ('status', 'is_published', 'is_private', 'pub_date'),
            'description': _('Configure o status e visibilidade do roadmap')
        }),
        (_('Autor'), {
            'fields': ('author',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['publish_roadmaps', 'unpublish_roadmaps', 'make_private', 'make_public', 'mark_as_completed']

    def get_title(self, obj):
        """Retorna o título em português ou o primeiro disponível"""
        pt_translation = obj.translations.filter(language='pt').first()
        if pt_translation:
            return pt_translation.title
        first_translation = obj.translations.first()
        if first_translation:
            return format_html(
                '<span style="color: #666;">[{}] {}</span>',
                first_translation.language.upper(),
                first_translation.title
            )
        return _('Sem tradução')
    get_title.short_description = _('Título')
    get_title.admin_order_field = 'translations__title'

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

    def publish_roadmaps(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(is_published=True, pub_date=timezone.now())
        self.message_user(request, _('{} roadmaps foram publicados.').format(updated))
    publish_roadmaps.short_description = _('Publicar roadmaps selecionados')

    def unpublish_roadmaps(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, _('{} roadmaps foram despublicados.').format(updated))
    unpublish_roadmaps.short_description = _('Despublicar roadmaps selecionados')

    def make_private(self, request, queryset):
        updated = queryset.update(is_private=True)
        self.message_user(request, _('{} roadmaps foram tornados privados.').format(updated))
    make_private.short_description = _('Tornar privados')

    def make_public(self, request, queryset):
        updated = queryset.update(is_private=False)
        self.message_user(request, _('{} roadmaps foram tornados públicos.').format(updated))
    make_public.short_description = _('Tornar públicos')

    def mark_as_completed(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, _('{} roadmaps foram marcados como concluídos.').format(updated))
    mark_as_completed.short_description = _('Marcar como concluídos')

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.roadmap = form.instance
            instance.save()
        formset.save_m2m()

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('translations')

    class Media:
        css = {
            'all': ('admin/css/roadmap_admin.css',)
        }
        js = ('admin/js/roadmap_admin.js',)


@admin.register(RoadmapTranslation)
class RoadmapTranslationAdmin(BaseModelAdmin):
    list_display = ('roadmap', 'language', 'title', 'get_content_preview', 'created_at')
    list_filter = ('language', 'created_at', 'roadmap__status')
    search_fields = ('title', 'content', 'summary', 'roadmap__translations__title')
    autocomplete_fields = ['roadmap']
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Roadmap'), {
            'fields': ('roadmap',)
        }),
        (_('Tradução'), {
            'fields': ('language', 'title', 'summary', 'content'),
            'description': _('Conteúdo da tradução')
        }),
    )
    
    def get_content_preview(self, obj):
        if obj.content:
            return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
        return _('Sem conteúdo')
    get_content_preview.short_description = _('Preview do Conteúdo')
