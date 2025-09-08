from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from core.admin import BaseModelAdmin
from .models import *


@admin.register(Solicitation)
class SolicitationAdmin(BaseModelAdmin):
    list_display = ('protocol', 'title', 'status', 'category', 'priority', 'user', 'assigned_to', 'created_at')
    list_filter = ('status', 'category', 'priority', 'created_at', 'assigned_to')
    search_fields = ('protocol', 'title', 'description', 'user__username', 'user__email')
    ordering = ('-created_at',)
    readonly_fields = ('protocol', 'created_at', 'updated_at', 'resolved_at', 'closed_at')
    fieldsets = (
        (_('Informações Básicas'), {
            'fields': ('protocol', 'title', 'description', 'user')
        }),
        (_('Classificação'), {
            'fields': ('status', 'category', 'priority')
        }),
        (_('Atribuição'), {
            'fields': ('assigned_to',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'resolved_at', 'closed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Staff vê apenas suas próprias solicitações atribuídas
        return qs.filter(assigned_to=request.user)


@admin.register(SolicitationHistory)
class SolicitationHistoryAdmin(BaseModelAdmin):
    list_display = ('solicitation', 'action', 'timestamp', 'user')
    search_fields = ('solicitation__protocol', 'solicitation__title', 'action', 'user__username')
    list_filter = ('timestamp', 'user', 'solicitation__status')
    readonly_fields = ('timestamp',)
    ordering = ('-timestamp',)


@admin.register(SolicitationParticipant)
class SolicitationParticipantAdmin(BaseModelAdmin):
    list_display = ('user', 'solicitation', 'solicitation_protocol', 'user_email')
    search_fields = ('user__username', 'user__email', 'solicitation__protocol', 'solicitation__title')
    list_filter = ('solicitation__status', 'solicitation__category')

    def solicitation_protocol(self, obj):
        return obj.solicitation.protocol
    solicitation_protocol.short_description = _('Protocolo da Solicitação')

    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = _('Email do Usuário')
