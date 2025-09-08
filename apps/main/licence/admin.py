from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import License, LicenseVerification
from core.admin import BaseModelAdmin


@admin.register(License)
class LicenseAdmin(BaseModelAdmin):
    icon = 'fas fa-key'
    list_display = [
        'license_key_short', 'license_type_with_icon', 'domain', 'company_name', 
        'status_with_icon', 'activated_at', 'expires_at', 'verification_count'
    ]
    list_filter = ['license_type', 'status', 'activated_at', 'expires_at']
    search_fields = ['license_key', 'domain', 'company_name', 'contact_email']
    readonly_fields = [
        'license_key', 'verification_count', 'last_verification', 
        'created_at', 'updated_at', 'license_type', 'status', 'domain', 'company_name',
        'contact_email', 'contact_phone', 'contract_number', 'support_hours_used',
        'support_hours_limit', 'activated_at', 'expires_at', 'features_enabled', 'notes'
    ]
    
    fieldsets = (
        (_('Informações da Licença'), {
            'fields': ('license_key', 'license_type', 'status')
        }),
        (_('Cliente'), {
            'fields': ('domain', 'company_name', 'contact_email', 'contact_phone')
        }),
        (_('Contrato (PDL PRO)'), {
            'fields': ('contract_number', 'support_hours_used', 'support_hours_limit'),
            'classes': ('collapse',)
        }),
        (_('Datas'), {
            'fields': ('activated_at', 'expires_at', 'last_verification'),
            'classes': ('collapse',)
        }),
        (_('Funcionalidades'), {
            'fields': ('features_enabled',),
            'classes': ('collapse',)
        }),
        (_('Estatísticas'), {
            'fields': ('verification_count',),
            'classes': ('collapse',)
        }),
        (_('Observações'), {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        (_('Metadados'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = None  # Remove ações em massa

    def license_key_short(self, obj):
        """Exibe apenas os primeiros caracteres da chave de licença"""
        if obj.license_key:
            return format_html(
                '<i class="fas fa-key text-primary"></i> <code>{}</code>',
                obj.license_key[:12] + "..."
            )
        return "-"
    license_key_short.short_description = _("Chave de Licença")
    
    def license_type_with_icon(self, obj):
        """Exibe o tipo de licença com ícone"""
        if obj.license_type == 'free':
            return format_html(
                '<i class="fas fa-gift text-info"></i> <span class="badge bg-info">PDL FREE</span>'
            )
        else:
            return format_html(
                '<i class="fas fa-crown text-warning"></i> <span class="badge bg-warning">PDL PRO</span>'
            )
    license_type_with_icon.short_description = _("Tipo")
    
    def status_with_icon(self, obj):
        """Exibe o status com ícone"""
        if obj.status == 'active':
            return format_html(
                '<i class="fas fa-check-circle text-success"></i> <span class="badge bg-success">Ativa</span>'
            )
        elif obj.status == 'expired':
            return format_html(
                '<i class="fas fa-exclamation-triangle text-danger"></i> <span class="badge bg-danger">Expirada</span>'
            )
        elif obj.status == 'suspended':
            return format_html(
                '<i class="fas fa-pause-circle text-warning"></i> <span class="badge bg-warning">Suspensa</span>'
            )
        else:
            return format_html(
                '<i class="fas fa-times-circle text-secondary"></i> <span class="badge bg-secondary">Inativa</span>'
            )
    status_with_icon.short_description = _("Status")
    
    def activate_licenses(self, request, queryset):
        """Ação para ativar licenças selecionadas"""
        count = 0
        for license in queryset:
            if license.status != 'active':
                license.activate(license.domain)
                count += 1
        
        self.message_user(
            request, 
            f"{count} licença(s) ativada(s) com sucesso."
        )
    activate_licenses.short_description = _("Ativar licenças selecionadas")
    
    def deactivate_licenses(self, request, queryset):
        """Ação para desativar licenças selecionadas"""
        count = 0
        for license in queryset:
            if license.status == 'active':
                license.deactivate()
                count += 1
        
        self.message_user(
            request, 
            f"{count} licença(s) desativada(s) com sucesso."
        )
    deactivate_licenses.short_description = _("Desativar licenças selecionadas")
    
    def renew_licenses(self, request, queryset):
        """Ação para renovar licenças selecionadas"""
        count = 0
        for license in queryset:
            license.renew(365)  # Renova por 1 ano
            count += 1
        
        self.message_user(
            request, 
            f"{count} licença(s) renovada(s) por 365 dias."
        )
    renew_licenses.short_description = _("Renovar licenças por 1 ano")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(LicenseVerification)
class LicenseVerificationAdmin(BaseModelAdmin):
    icon = 'fas fa-shield-alt'
    list_display = [
        'license_domain', 'verification_date', 'ip_address', 
        'success_with_icon', 'response_time_with_icon'
    ]
    list_filter = ['success', 'verification_date', 'license__license_type']
    search_fields = ['license__domain', 'license__license_key', 'ip_address']
    readonly_fields = [
        'license', 'verification_date', 'ip_address', 'user_agent',
        'success', 'error_message', 'response_time'
    ]
    
    fieldsets = (
        (_('Licença'), {
            'fields': ('license',)
        }),
        (_('Verificação'), {
            'fields': ('verification_date', 'success', 'response_time')
        }),
        (_('Detalhes da Requisição'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Erro (se houver)'), {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
    )
    
    def license_domain(self, obj):
        """Exibe o domínio da licença"""
        if obj.license:
            return format_html(
                '<i class="fas fa-globe text-primary"></i> <strong>{}</strong>',
                obj.license.domain
            )
        return "-"
    license_domain.short_description = _("Domínio")
    
    def success_with_icon(self, obj):
        """Exibe o sucesso da verificação com ícone"""
        if obj.success:
            return format_html(
                '<i class="fas fa-check-circle text-success"></i> <span class="badge bg-success">Sucesso</span>'
            )
        else:
            return format_html(
                '<i class="fas fa-times-circle text-danger"></i> <span class="badge bg-danger">Falha</span>'
            )
    success_with_icon.short_description = _("Resultado")
    
    def response_time_with_icon(self, obj):
        """Exibe o tempo de resposta com ícone"""
        if obj.response_time is not None:
            try:
                # Ensure we're working with a float value
                response_time = float(obj.response_time)
                if response_time < 1.0:
                    color = 'success'
                    icon = 'fas fa-bolt'
                elif response_time < 3.0:
                    color = 'warning'
                    icon = 'fas fa-clock'
                else:
                    color = 'danger'
                    icon = 'fas fa-hourglass-half'
                
                # Format the time as string first, then use it in format_html
                time_str = f"{response_time:.2f}s"
                return format_html(
                    '<i class="{} text-{}"></i> <span class="text-{}">{}</span>',
                    icon, color, color, time_str
                )
            except (ValueError, TypeError):
                return "-"
        return "-"
    response_time_with_icon.short_description = _("Tempo de Resposta")
    
    def has_add_permission(self, request):
        """Não permite adicionar verificações manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Não permite editar verificações"""
        return False
