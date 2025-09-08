from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from core.admin import BaseModelAdmin
from .models import *


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 0
    readonly_fields = ('item_name', 'item_id', 'quantidade', 'preco_unitario', 'preco_total', 'tipo_compra', 'nome_pacote')
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(ShopItem)
class ShopItemAdmin(BaseModelAdmin):
    list_display = ('nome', 'item_id', 'quantidade', 'preco', 'ativo', 'created_at')
    list_filter = ('ativo', 'created_at', 'preco')
    search_fields = ('nome', 'item_id')
    ordering = ('nome',)
    list_editable = ('ativo', 'preco', 'quantidade')
    
    fieldsets = (
        (_('Informações do Item'), {
            'fields': ('nome', 'item_id', 'quantidade')
        }),
        (_('Preços e Status'), {
            'fields': ('preco', 'ativo'),
            'description': _('Configure o preço e status de disponibilidade')
        }),
    )
    
    actions = ['activate_items', 'deactivate_items', 'update_prices']


@admin.register(ShopPackage)
class ShopPackageAdmin(BaseModelAdmin):
    list_display = ('nome', 'preco_total', 'ativo', 'promocao', 'get_items_count', 'created_at')
    list_filter = ('ativo', 'promocao', 'created_at')
    search_fields = ('nome',)
    ordering = ('nome',)
    list_editable = ('ativo', 'promocao')
    
    fieldsets = (
        (_('Informações do Pacote'), {
            'fields': ('nome', 'preco_total')
        }),
        (_('Status'), {
            'fields': ('ativo', 'promocao'),
            'description': _('Configure a disponibilidade e promoções')
        }),
    )
    
    actions = ['activate_packages', 'deactivate_packages', 'apply_promotion']
    
    def get_items_count(self, obj):
        return obj.shoppackageitem_set.count()
    get_items_count.short_description = _('Itens')


@admin.register(PromotionCode)
class PromotionCodeAdmin(BaseModelAdmin):
    list_display = ('codigo', 'desconto_percentual', 'ativo', 'validade', 'apoiador', 'created_at')
    search_fields = ('codigo', 'apoiador__nome_publico')
    list_filter = ('ativo', 'validade', 'created_at')
    list_editable = ('ativo', 'desconto_percentual')
    
    fieldsets = (
        (_('Informações do Código'), {
            'fields': ('codigo', 'desconto_percentual', 'apoiador')
        }),
        (_('Validade'), {
            'fields': ('ativo', 'validade'),
            'description': _('Configure quando o código estará ativo')
        }),
    )
    
    actions = ['activate_codes', 'deactivate_codes']


@admin.register(Cart)
class CartAdmin(BaseModelAdmin):
    list_display = ('user', 'usar_bonus', 'promocao_aplicada', 'calcular_total', 'get_items_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
    list_filter = ('usar_bonus', 'promocao_aplicada', 'created_at')
    
    fieldsets = (
        (_('Usuário'), {
            'fields': ('user',)
        }),
        (_('Informações Básicas'), {
            'fields': ('promocao_aplicada',)
        }),
        (_('Pagamento com Bônus'), {
            'fields': ('usar_bonus', 'valor_bonus_usado', 'valor_dinheiro_usado'),
            'description': _('Configurações de pagamento misto')
        }),
    )
    
    def get_items_count(self, obj):
        return obj.cartitem_set.count() + obj.cartpackage_set.count()
    get_items_count.short_description = _('Itens')


@admin.register(ShopPurchase)
class ShopPurchaseAdmin(BaseModelAdmin):
    list_display = ('user', 'character_name', 'total_pago', 'valor_bonus_usado', 'valor_dinheiro_usado', 'data_compra', 'get_items_count', 'status_pagamento')
    list_filter = ('data_compra', 'promocao_aplicada', 'apoiador', 'created_at')
    search_fields = ('user__username', 'character_name', 'user__email')
    ordering = ('-data_compra',)
    inlines = [PurchaseItemInline]
    readonly_fields = ('data_compra', 'total_pago')
    
    fieldsets = (
        (_('Informações da Compra'), {
            'fields': ('user', 'character_name', 'data_compra')
        }),
        (_('Detalhes do Pagamento'), {
            'fields': ('total_pago', 'valor_bonus_usado', 'valor_dinheiro_usado'),
            'description': _('Como foi realizado o pagamento')
        }),
        (_('Promoções'), {
            'fields': ('promocao_aplicada', 'apoiador')
        }),
    )
    
    actions = ['mark_as_paid', 'mark_as_pending', 'export_purchases']
    
    def get_items_count(self, obj):
        """Retorna o número de itens na compra"""
        return obj.items.count()
    get_items_count.short_description = _('Itens')
    get_items_count.admin_order_field = 'items__count'
    
    def status_pagamento(self, obj):
        if obj.total_pago > 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                _('Pago')
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            _('Pendente')
        )
    status_pagamento.short_description = _('Status')


@admin.register(ShopPackageItem)
class ShopPackageItemAdmin(BaseModelAdmin):
    list_display = ('pacote', 'item', 'quantidade', 'created_at')
    search_fields = ('pacote__nome', 'item__nome')
    ordering = ('pacote', 'item')
    list_filter = ('quantidade', 'created_at')
    
    fieldsets = (
        (_('Pacote e Item'), {
            'fields': ('pacote', 'item')
        }),
        (_('Quantidade'), {
            'fields': ('quantidade',)
        }),
    )


@admin.register(CartItem)
class CartItemAdmin(BaseModelAdmin):
    list_display = ('cart', 'item', 'quantidade', 'get_total_price', 'created_at')
    search_fields = ('cart__user__username', 'item__nome')
    ordering = ('-created_at',)
    list_filter = ('quantidade', 'created_at')
    
    fieldsets = (
        (_('Carrinho e Item'), {
            'fields': ('cart', 'item')
        }),
        (_('Quantidade'), {
            'fields': ('quantidade',)
        }),
    )
    
    def get_total_price(self, obj):
        return obj.item.preco * obj.quantidade
    get_total_price.short_description = _('Total')


@admin.register(CartPackage)
class CartPackageAdmin(BaseModelAdmin):
    list_display = ('cart', 'pacote', 'quantidade', 'get_total_price', 'created_at')
    search_fields = ('cart__user__username', 'pacote__nome')
    ordering = ('-created_at',)
    list_filter = ('quantidade', 'created_at')
    
    fieldsets = (
        (_('Carrinho e Pacote'), {
            'fields': ('cart', 'pacote')
        }),
        (_('Quantidade'), {
            'fields': ('quantidade',)
        }),
    )
    
    def get_total_price(self, obj):
        return obj.pacote.preco_total * obj.quantidade
    get_total_price.short_description = _('Total')


@admin.register(PurchaseItem)
class PurchaseItemAdmin(BaseModelAdmin):
    list_display = ('purchase', 'item_name', 'item_id', 'quantidade', 'preco_unitario', 'preco_total', 'tipo_compra', 'nome_pacote', 'created_at')
    list_filter = ('tipo_compra', 'purchase__data_compra', 'purchase__user', 'created_at')
    search_fields = ('item_name', 'purchase__user__username', 'purchase__character_name', 'nome_pacote')
    ordering = ('-purchase__data_compra', 'item_name')
    readonly_fields = ('purchase', 'item_name', 'item_id', 'quantidade', 'preco_unitario', 'preco_total', 'tipo_compra', 'nome_pacote')
    
    fieldsets = (
        (_('Informações da Compra'), {
            'fields': ('purchase',)
        }),
        (_('Detalhes do Item'), {
            'fields': ('item_name', 'item_id', 'quantidade', 'tipo_compra', 'nome_pacote')
        }),
        (_('Informações de Preço'), {
            'fields': ('preco_unitario', 'preco_total'),
            'description': _('Valores registrados no momento da compra')
        }),
    )
    
    def has_add_permission(self, request):
        """Desabilita a criação manual de itens de compra"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Desabilita a edição de itens de compra"""
        return False
