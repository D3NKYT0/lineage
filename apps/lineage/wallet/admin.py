from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Wallet, TransacaoWallet, TransacaoBonus, CoinConfig, CoinPurchaseBonus
from core.admin import BaseModelAdmin


@admin.register(Wallet)
class WalletAdmin(BaseModelAdmin):
    list_display = ['usuario', 'saldo', 'saldo_bonus', 'get_total_balance', 'created_at']
    search_fields = ['usuario__username', 'usuario__email']
    list_filter = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Usuário'), {
            'fields': ('usuario',)
        }),
        (_('Saldos'), {
            'fields': ('saldo', 'saldo_bonus'),
            'description': _('Saldos atuais da carteira')
        }),
    )
    
    def get_total_balance(self, obj):
        total = obj.saldo + obj.saldo_bonus
        if total > 0:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">R$ {}</span>',
                f"{total:.2f}"
            )
        return format_html(
            '<span style="color: #dc3545;">R$ {}</span>',
            f"{total:.2f}"
        )
    get_total_balance.short_description = _('Saldo Total')


@admin.register(TransacaoWallet)
class TransacaoWalletAdmin(BaseModelAdmin):
    list_display = ['wallet', 'tipo', 'valor', 'descricao', 'data', 'get_formatted_value']
    list_filter = ['tipo', 'data', 'created_at']
    search_fields = ['wallet__usuario__username', 'descricao']
    ordering = ['-data', '-created_at']
    readonly_fields = ['data']
    
    fieldsets = (
        (_('Carteira'), {
            'fields': ('wallet',)
        }),
        (_('Transação'), {
            'fields': ('tipo', 'valor', 'descricao')
        }),
        (_('Informações da Transação'), {
            'fields': ('data',),
            'description': _('Data automaticamente definida quando a transação é criada'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_transactions']
    
    def get_formatted_value(self, obj):
        if obj.tipo == 'credito':
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">+R$ {}</span>',
                f"{obj.valor:.2f}"
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">-R$ {}</span>',
                f"{obj.valor:.2f}"
            )
    get_formatted_value.short_description = _('Valor Formatado')


@admin.register(TransacaoBonus)
class TransacaoBonusAdmin(BaseModelAdmin):
    list_display = ['wallet', 'tipo', 'valor', 'descricao', 'data', 'get_formatted_value']
    list_filter = ['tipo', 'data', 'created_at']
    search_fields = ['wallet__usuario__username', 'descricao']
    ordering = ['-data', '-created_at']
    readonly_fields = ['data']
    
    fieldsets = (
        (_('Carteira'), {
            'fields': ('wallet',)
        }),
        (_('Transação'), {
            'fields': ('tipo', 'valor', 'descricao')
        }),
        (_('Informações da Transação'), {
            'fields': ('data',),
            'description': _('Data automaticamente definida quando a transação é criada'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['export_bonus_transactions']
    
    def get_formatted_value(self, obj):
        if obj.tipo == 'credito':
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">+{} bônus</span>',
                f"{obj.valor:.0f}"
            )
        else:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">-{} bônus</span>',
                f"{obj.valor:.0f}"
            )
    get_formatted_value.short_description = _('Valor Formatado')


@admin.register(CoinConfig)
class CoinConfigAdmin(BaseModelAdmin):
    list_display = ('nome', 'coin_id', 'multiplicador', 'ativa', 'created_at')
    list_filter = ('ativa', 'multiplicador', 'created_at')
    search_fields = ('nome', 'coin_id')
    ordering = ('nome',)
    list_editable = ('ativa', 'multiplicador')
    
    fieldsets = (
        (_('Informações da Moeda'), {
            'fields': ('nome', 'coin_id')
        }),
        (_('Configurações'), {
            'fields': ('multiplicador', 'ativa'),
            'description': _('Configure o multiplicador e status da moeda')
        }),
    )
    
    actions = ['activate_coins', 'deactivate_coins']


@admin.register(CoinPurchaseBonus)
class CoinPurchaseBonusAdmin(BaseModelAdmin):
    list_display = ('descricao', 'valor_minimo', 'valor_maximo', 'bonus_percentual', 'ativo', 'ordem', 'created_at')
    list_filter = ('ativo', 'bonus_percentual', 'created_at')
    list_editable = ('ativo', 'ordem', 'bonus_percentual')
    search_fields = ('descricao',)
    ordering = ('ordem', 'valor_minimo')
    
    fieldsets = (
        (_('Configuração Básica'), {
            'fields': ('descricao', 'ativo', 'ordem')
        }),
        (_('Faixa de Valores'), {
            'fields': ('valor_minimo', 'valor_maximo'),
            'description': _('Configure a faixa de valores para aplicar o bônus')
        }),
        (_('Bônus'), {
            'fields': ('bonus_percentual',),
            'description': _('Percentual de bônus a ser aplicado')
        }),
    )
    
    actions = ['activate_bonuses', 'deactivate_bonuses', 'reorder_bonuses']
    
    def reorder_bonuses(self, request, queryset):
        """Reordena os bônus baseado na ordem atual"""
        for i, bonus in enumerate(queryset.order_by('ordem'), 1):
            bonus.ordem = i
            bonus.save()
        self.message_user(request, _('Ordem dos bônus foi reorganizada.'))
    reorder_bonuses.short_description = _('Reorganizar ordem')
