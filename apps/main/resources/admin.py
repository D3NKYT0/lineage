from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from core.admin import BaseModelAdmin
from .models import SystemResource


@admin.register(SystemResource)
class SystemResourceAdmin(BaseModelAdmin):
    list_display = [
        'display_name', 'name', 'category', 'is_active', 'order', 'get_status_badge'
    ]
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'display_name', 'description']
    list_editable = ['is_active', 'order']
    ordering = ['category', 'order', 'display_name']
    
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('name', 'display_name', 'description')
        }),
        (_('Configurações'), {
            'fields': ('category', 'is_active', 'order', 'icon'),
            'description': _('Configure a categoria, status e ordem de exibição do recurso')
        }),
    )
    
    actions = ['activate_resources', 'deactivate_resources']
    
    def get_status_badge(self, obj):
        """Exibe um badge colorido para o status do recurso"""
        if obj.is_active:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
                _('Ativo')
            )
        else:
            return format_html(
                '<span style="background: #dc3545; color: white; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">{}</span>',
                _('Inativo')
            )
    get_status_badge.short_description = _('Status')
    get_status_badge.admin_order_field = 'is_active'
    
    def activate_resources(self, request, queryset):
        """Ação para ativar recursos selecionados"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            _('{} recursos foram ativados com sucesso.').format(updated),
            level='SUCCESS'
        )
    activate_resources.short_description = _('Ativar recursos selecionados')
    
    def deactivate_resources(self, request, queryset):
        """Ação para desativar recursos selecionados"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            _('{} recursos foram desativados com sucesso.').format(updated),
            level='WARNING'
        )
    deactivate_resources.short_description = _('Desativar recursos selecionados')
