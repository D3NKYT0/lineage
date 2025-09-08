from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import *
from core.admin import BaseModelAdmin
from .forms import BoxTypeAdminForm


@admin.register(Prize)
class PrizeAdmin(BaseModelAdmin):
    list_display = ('name', 'image_preview', 'weight', 'item_id', 'enchant', 'rarity', 'created_at', 'updated_at')
    search_fields = ('name', 'item_id')
    list_filter = ('created_at', 'rarity', 'enchant')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('name',)
    
    fieldsets = (
        (_('Informações do Prêmio'), {
            'fields': ('name', 'item_id', 'image', 'weight', 'enchant', 'rarity')
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" style="object-fit: contain; border: 1px solid #ccc; border-radius: 6px;" />',
            obj.get_image_url()
        )
    image_preview.short_description = _('Imagem')


@admin.register(SpinHistory)
class SpinHistoryAdmin(BaseModelAdmin):
    list_display = ('user', 'prize', 'created_at', 'get_prize_rarity')
    search_fields = ('user__username', 'prize__name')
    list_filter = ('created_at', 'prize__rarity')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Usuário e Prêmio'), {
            'fields': ('user', 'prize')
        }),
        (_('Data'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_prize_rarity(self, obj):
        rarity_colors = {
            'common': '#6c757d',
            'rare': '#007bff',
            'epic': '#6f42c1',
            'legendary': '#fd7e14'
        }
        color = rarity_colors.get(obj.prize.rarity, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.prize.get_rarity_display()
        )
    get_prize_rarity.short_description = _('Raridade')


@admin.register(Bag)
class BagAdmin(BaseModelAdmin):
    list_display = ('user', 'get_items_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Usuário'), {
            'fields': ('user',)
        }),
        (_('Data'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_items_count(self, obj):
        return obj.items.count()
    get_items_count.short_description = _('Itens')


@admin.register(BagItem)
class BagItemAdmin(BaseModelAdmin):
    list_display = ('bag', 'item_name', 'enchant', 'quantity', 'added_at')
    search_fields = ('item_name', 'bag__user__username')
    list_filter = ('enchant', 'added_at', 'quantity')
    readonly_fields = ('added_at',)
    ordering = ('-added_at',)
    
    fieldsets = (
        (_('Bag e Item'), {
            'fields': ('bag', 'item_name', 'enchant', 'quantity')
        }),
        (_('Data'), {
            'fields': ('added_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Item)
class ItemAdmin(BaseModelAdmin):
    list_display = ('name', 'item_id', 'enchant', 'rarity', 'can_be_populated', 'description')
    list_editable = ('can_be_populated',)
    search_fields = ('name', 'item_id', 'description')
    list_filter = ('rarity', 'enchant', 'can_be_populated')
    ordering = ('name',)
    
    fieldsets = (
        (_('Informações do Item'), {
            'fields': ('name', 'item_id', 'enchant', 'rarity', 'description')
        }),
        (_('Configurações'), {
            'fields': ('can_be_populated',),
            'description': _('Define se o item pode ser populado automaticamente')
        }),
    )


@admin.register(BoxType)
class BoxTypeAdmin(BaseModelAdmin):
    form = BoxTypeAdminForm
    
    list_display = (
        'name', 'price', 'boosters_amount',
        'chance_common', 'chance_rare', 'chance_epic', 'chance_legendary',
        'max_epic_items', 'max_legendary_items', 'get_items_count'
    )
    search_fields = ('name',)
    list_filter = ('price', 'boosters_amount', 'chance_legendary')
    ordering = ('name',)
    filter_horizontal = ('allowed_items',)

    fieldsets = (
        (_('Informações Básicas'), {
            'fields': (
                'name', 'price', 'boosters_amount',
                'allowed_items'
            )
        }),
        (_('Chances de Raridade (%)'), {
            'fields': (
                'chance_common', 'chance_rare',
                'chance_epic', 'chance_legendary'
            ),
            'description': _('Configure as chances de cada raridade (total deve ser 100%)')
        }),
        (_('Limites por Raridade'), {
            'fields': (
                'max_epic_items', 'max_legendary_items',
            ),
            'description': _('Limite máximo de itens por raridade')
        }),
    )
    
    def get_items_count(self, obj):
        return obj.allowed_items.count()
    get_items_count.short_description = _('Itens Permitidos')


@admin.register(Box)
class BoxAdmin(BaseModelAdmin):
    list_display = ('user', 'box_type', 'opened', 'created_at', 'get_prize_info')
    search_fields = ('user__username', 'box_type__name')
    list_filter = ('opened', 'created_at', 'box_type')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Usuário e Tipo'), {
            'fields': ('user', 'box_type')
        }),
        (_('Status'), {
            'fields': ('opened',),
            'description': _('Se a caixa foi aberta')
        }),
        (_('Data'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_prize_info(self, obj):
        if obj.opened:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                _('Aberta')
            )
        return format_html(
            '<span style="background: #ffc107; color: black; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            _('Fechada')
        )
    get_prize_info.short_description = _('Status')


@admin.register(BoxItem)
class BoxItemAdmin(BaseModelAdmin):
    list_display = ('box', 'item', 'opened', 'probability', 'created_at')
    search_fields = ('box__user__username', 'item__name')
    list_filter = ('opened', 'created_at')
    ordering = ('box', 'item')
    
    fieldsets = (
        (_('Box e Item'), {
            'fields': ('box', 'item')
        }),
        (_('Configurações'), {
            'fields': ('opened', 'probability'),
            'description': _('Probabilidade de obter este item')
        }),
    )


@admin.register(BoxItemHistory)
class BoxItemHistoryAdmin(BaseModelAdmin):
    list_display = ('user', 'item', 'enchant', 'rarity', 'box', 'obtained_at', 'get_rarity_badge')
    list_filter = ('rarity', 'obtained_at', 'enchant')
    search_fields = ('user__username', 'item__name')
    ordering = ('-obtained_at',)
    readonly_fields = ('user', 'item', 'box', 'rarity', 'enchant', 'obtained_at')
    
    fieldsets = (
        (_('Usuário e Item'), {
            'fields': ('user', 'item', 'enchant', 'rarity')
        }),
        (_('Box'), {
            'fields': ('box',)
        }),
        (_('Data'), {
            'fields': ('obtained_at',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
    
    def get_rarity_badge(self, obj):
        rarity_colors = {
            'common': '#6c757d',
            'rare': '#007bff',
            'epic': '#6f42c1',
            'legendary': '#fd7e14'
        }
        color = rarity_colors.get(obj.rarity, '#6c757d')
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_rarity_display()
        )
    get_rarity_badge.short_description = _('Raridade')


@admin.register(Recompensa)
class RecompensaAdmin(BaseModelAdmin):
    list_display = ('tipo', 'referencia', 'item_name', 'quantity', 'enchant', 'created_at')
    list_filter = ('tipo', 'enchant', 'created_at')
    search_fields = ('referencia', 'item_name')
    ordering = ('tipo', 'referencia')
    
    fieldsets = (
        (_('Informações da Recompensa'), {
            'fields': ('tipo', 'referencia', 'item_name', 'quantity', 'enchant')
        }),
    )


@admin.register(RecompensaRecebida)
class RecompensaRecebidaAdmin(BaseModelAdmin):
    list_display = ('user', 'recompensa', 'data', 'created_at')
    list_filter = ('data', 'created_at', 'recompensa__tipo')
    search_fields = ('user__username', 'recompensa__item_name', 'recompensa__tipo')
    ordering = ('-data',)
    readonly_fields = ('data',)
    
    fieldsets = (
        (_('Usuário e Recompensa'), {
            'fields': ('user', 'recompensa')
        }),
        (_('Informações da Recompensa'), {
            'fields': ('data',),
            'description': _('Data automaticamente definida quando a recompensa é recebida'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EconomyWeapon)
class EconomyWeaponAdmin(BaseModelAdmin):
    list_display = ('user', 'level', 'fragments', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('level', 'created_at')
    ordering = ('-level',)
    
    fieldsets = (
        (_('Usuário'), {
            'fields': ('user',)
        }),
        (_('Progresso'), {
            'fields': ('level', 'fragments'),
            'description': _('Nível atual e fragmentos coletados')
        }),
    )


@admin.register(Monster)
class MonsterAdmin(BaseModelAdmin):
    list_display = ('name', 'level', 'required_weapon_level', 'fragment_reward', 'respawn_seconds', 'is_alive_display', 'created_at')
    readonly_fields = ('last_defeated_at',)
    search_fields = ('name',)
    list_filter = ('level', 'required_weapon_level', 'created_at')
    ordering = ('level', 'name')
    
    fieldsets = (
        (_('Informações do Monstro'), {
            'fields': ('name', 'level', 'required_weapon_level')
        }),
        (_('Recompensas'), {
            'fields': ('fragment_reward', 'respawn_seconds'),
            'description': _('Fragmentos ganhos e tempo de respawn')
        }),
        (_('Status'), {
            'fields': ('last_defeated_at',),
            'classes': ('collapse',)
        }),
    )

    def is_alive_display(self, obj):
        return obj.is_alive
    is_alive_display.boolean = True
    is_alive_display.short_description = _("Disponível para Luta")


@admin.register(RewardItem)
class RewardItemAdmin(BaseModelAdmin):
    list_display = ('name', 'item_id', 'enchant', 'description', 'amount', 'created_at')
    search_fields = ('name', 'item_id', 'description')
    list_filter = ('enchant', 'created_at')
    ordering = ('name',)

    fieldsets = (
        (_('Informações do Item'), {
            'fields': ('name', 'item_id', 'enchant', 'description', 'amount')
        }),
    )


@admin.register(BattlePassSeason)
class BattlePassSeasonAdmin(BaseModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active', 'get_duration')
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name',)
    ordering = ('-start_date',)
    
    fieldsets = (
        (_('Informações da Temporada'), {
            'fields': ('name', 'start_date', 'end_date')
        }),
        (_('Status'), {
            'fields': ('is_active',),
            'description': _('Se a temporada está ativa')
        }),
    )
    
    def get_duration(self, obj):
        if obj.start_date and obj.end_date:
            duration = obj.end_date - obj.start_date
            return f"{duration.days} dias"
        return _('N/A')
    get_duration.short_description = _('Duração')


class BattlePassRewardInline(admin.TabularInline):
    model = BattlePassReward
    extra = 1
    fields = ('description', 'is_premium', 'item_id', 'item_name', 'item_enchant', 'item_amount')


@admin.register(BattlePassLevel)
class BattlePassLevelAdmin(BaseModelAdmin):
    list_display = ('season', 'level', 'required_xp', 'get_rewards_count')
    list_filter = ('season', 'level')
    ordering = ('season', 'level')
    inlines = [BattlePassRewardInline]
    
    fieldsets = (
        (_('Informações do Nível'), {
            'fields': ('season', 'level', 'required_xp')
        }),
    )

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.level = form.instance
            instance.save()
        formset.save_m2m()
    
    def get_rewards_count(self, obj):
        return obj.battlepassreward_set.count()
    get_rewards_count.short_description = _('Recompensas')


@admin.register(BattlePassReward)
class BattlePassRewardAdmin(BaseModelAdmin):
    list_display = ('level', 'description', 'is_premium', 'item_name', 'item_amount', 'item_enchant', 'get_premium_badge')
    list_filter = ('is_premium', 'level__season', 'item_enchant')
    search_fields = ('description', 'item_name')
    ordering = ('level__season', 'level__level')
    
    fieldsets = (
        (_('Informações da Recompensa'), {
            'fields': ('level', 'description', 'is_premium')
        }),
        (_('Item da Recompensa'), {
            'fields': ('item_id', 'item_name', 'item_enchant', 'item_amount'),
            'classes': ('collapse',)
        }),
    )
    
    def get_premium_badge(self, obj):
        if obj.is_premium:
            return format_html(
                '<span style="background: #fd7e14; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                _('Premium')
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            _('Gratuita')
        )
    get_premium_badge.short_description = _('Tipo')


@admin.register(UserBattlePassProgress)
class UserBattlePassProgressAdmin(BaseModelAdmin):
    list_display = ('user', 'season', 'xp', 'has_premium', 'get_level', 'created_at')
    list_filter = ('season', 'has_premium', 'created_at')
    search_fields = ('user__username',)
    filter_horizontal = ('claimed_rewards',)
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('Usuário e Temporada'), {
            'fields': ('user', 'season')
        }),
        (_('Progresso'), {
            'fields': ('xp', 'has_premium'),
            'description': _('XP atual e status premium')
        }),
        (_('Recompensas Reclamadas'), {
            'fields': ('claimed_rewards',),
            'description': _('Recompensas já reclamadas pelo usuário')
        }),
    )
    
    def get_level(self, obj):
        # Calcular nível baseado no XP
        level = 1
        for bp_level in obj.season.battlepasslevel_set.order_by('level'):
            if obj.xp >= bp_level.required_xp:
                level = bp_level.level
            else:
                break
        return level
    get_level.short_description = _('Nível')


@admin.register(BattlePassItemExchange)
class BattlePassItemExchangeAdmin(BaseModelAdmin):
    list_display = ('item_name', 'item_enchant', 'xp_amount', 'is_active', 'current_exchanges', 'max_exchanges', 'created_at')
    list_filter = ('is_active', 'item_enchant', 'created_at')
    search_fields = ('item_name',)
    readonly_fields = ('current_exchanges',)
    ordering = ('item_name',)
    
    fieldsets = (
        (_('Informações do Item'), {
            'fields': ('item_id', 'item_name', 'item_enchant', 'xp_amount', 'is_active')
        }),
        (_('Limites de Troca'), {
            'fields': ('max_exchanges', 'current_exchanges'),
            'description': _('Defina 0 em max_exchanges para trocas ilimitadas')
        }),
    )
