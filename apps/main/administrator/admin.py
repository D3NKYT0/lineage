from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
from .forms import ThemeForm, ThemeVariableForm
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import helpers


@admin.register(ChatGroup)
class ChatGroupAdmin(BaseModelAdmin):
    list_display = ('group_name', 'sender', 'message_excerpt', 'timestamp')
    search_fields = ('group_name', 'sender__username', 'message')
    list_filter = ('group_name', 'timestamp')
    readonly_fields = ('timestamp',)

    def message_excerpt(self, obj):
        return obj.message[:20]
    message_excerpt.short_description = 'Message Excerpt'


@admin.register(Theme)
class ThemeAdmin(BaseModelAdmin):
    form = ThemeForm
    list_display = ('nome', 'slug', 'version', 'ativo')
    readonly_fields = ('nome', 'slug', 'version', 'author', 'descricao')
    fields = ('nome', 'slug', 'upload', 'version', 'author', 'descricao', 'ativo')
    actions = ['delete_selected_themes']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj.delete()

    def delete_selected_themes(self, request, queryset):
        if "post" in request.POST:
            count = queryset.count()
            for obj in queryset:
                obj.delete()
            self.message_user(request, f"{count} tema(s) deletado(s) com sucesso.", messages.SUCCESS)
            return None

        context = {
            'themes': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, "admin/themes/delete_confirmation.html", context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    delete_selected_themes.short_description = "Excluir temas selecionados"


@admin.register(BackgroundSetting)
class BackgroundSettingAdmin(BaseModelAdmin):
    list_display = ('name', 'is_active', 'image_preview')
    list_filter = ('is_active',)
    search_fields = ('name',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="200" style="object-fit: cover; border-radius: 8px;" />'
        return "(Sem imagem)"
    image_preview.allow_tags = True
    image_preview.short_description = "Preview"

    def save_model(self, request, obj, form, change):
        # Desativa todos os outros backgrounds se esse for ativado
        if obj.is_active:
            BackgroundSetting.objects.exclude(id=obj.id).update(is_active=False)
        super().save_model(request, obj, form, change)


@admin.register(ThemeVariable)
class ThemeVariableAdmin(BaseModelAdmin):
    form = ThemeVariableForm
    list_display = ('nome', 'tipo', 'criado_em', 'atualizado_em')
    list_filter = ('tipo',)
    search_fields = ('nome', 'valor_pt', 'valor_en', 'valor_es')
    ordering = ('nome',)
    readonly_fields = ('criado_em', 'atualizado_em')
    fieldsets = (
        (None, {
            'fields': ('nome', 'tipo', 'valor_pt', 'valor_en', 'valor_es')
        }),
        ('Datas', {
            'fields': ('criado_em', 'atualizado_em')
        }),
    )
