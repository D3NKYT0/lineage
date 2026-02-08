from django.contrib import admin
from .models import (
    ApiEndpointToggle, IndexConfig, IndexConfigTranslation, ComingSoonConfig,
    ServicePrice, ActiveAdenaExchangeItem, Apoiador, Comissao, ApoiadorDefault,
    ManagedLineageAccount, AccountLinkSlot, CustomTop,
    ItemInflationCategory, ItemInflationSnapshot, ItemInflationSnapshotDetail,
    ItemInflationStats, ItemInflationFavorite,
)
from core.admin import BaseModelAdmin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


@admin.register(ApiEndpointToggle)
class ApiEndpointToggleAdmin(BaseModelAdmin):
    list_display = [
        # Server endpoints
        'players_online', 'top_pvp', 'top_pk', 'top_clan', 'top_rich', 
        'top_online', 'top_level', 'olympiad_ranking', 'olympiad_all_heroes', 
        'olympiad_current_heroes', 'grandboss_status', 'raidboss_status', 
        'siege', 'siege_participants', 'boss_jewel_locations',
        # Authentication endpoints
        'auth_login', 'auth_refresh', 'auth_logout',
        # User endpoints
        'user_profile', 'user_change_password', 'user_dashboard', 'user_stats', 'user_game_data',
        # Search endpoints
        'search_character', 'search_item',
        # Game data endpoints
        'clan_detail', 'auction_items',
        # Server status endpoints
        'server_status',
        # API info endpoints
        'api_info',
        # Monitoring endpoints
        'health_check', 'hourly_metrics', 'daily_metrics', 'performance_metrics',
        'slow_queries', 'cache_stats',
        # Administration endpoints
        'api_config', 'api_config_panel',
    ]

    list_editable = list_display  # permite edição inline no list view
    list_display_links = None  # remove link para a edição detalhada
    actions = None  # remove ações em massa para evitar exclusões acidentais

    def has_add_permission(self, request):
        # Permite adicionar apenas se ainda não houver nenhum registro
        return not ApiEndpointToggle.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Impede a exclusão do registro
        return False


class IndexConfigTranslationInline(admin.TabularInline):
    model = IndexConfigTranslation
    extra = 1
    fields = ('language', 'nome_servidor', 'descricao_servidor', 'jogadores_online_texto')
    min_num = 1


@admin.register(IndexConfig)
class IndexConfigAdmin(BaseModelAdmin):
    list_display = (
        'nome_servidor', 'link_patch', 'link_cliente', 'link_discord', 
        'trailer_video_id', 'imagem_banner'
    )
    search_fields = ('nome_servidor',)
    list_filter = ()

    inlines = [IndexConfigTranslationInline]

    fieldsets = (
        (None, {
            'fields': ('nome_servidor', 'descricao_servidor', 'link_patch', 'link_cliente', 'link_discord')
        }),
        ('Configurações de Trailer', {
            'fields': ('trailer_video_id',)
        }),
        ('Configurações de Exibição', {
            'fields': ('jogadores_online_texto', 'imagem_banner')
        }),
    )

    def has_add_permission(self, request):
        return not IndexConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change and IndexConfig.objects.exists():
            self.message_user(
                request,
                "Apenas um registro de configuração do servidor pode existir. Por favor, edite o existente.",
                messages.WARNING
            )
            return
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.config = form.instance  # Ensure FK is set
            instance.save()
        formset.save_m2m()


@admin.register(ComingSoonConfig)
class ComingSoonConfigAdmin(BaseModelAdmin):
    list_display = ('title', 'is_active', 'staff_only_login', 'countdown_date', 'overlay_opacity')
    list_editable = ('is_active', 'staff_only_login')
    list_filter = ('is_active',)
    fieldsets = (
        (_('Ativação'), {
            'fields': ('is_active', 'staff_only_login'),
            'description': _('Quando ativo, a página inicial do site exibe a tela Coming Soon. Se "Apenas staff pode fazer login" estiver marcado, somente equipe conseguirá logar durante a contagem.')
        }),
        (_('Textos'), {
            'fields': ('title', 'subtitle')
        }),
        (_('Contagem regressiva'), {
            'fields': ('countdown_date', 'show_seconds')
        }),
        (_('Aparência'), {
            'fields': ('background_image', 'overlay_opacity', 'primary_color', 'secondary_color')
        }),
        (_('CSS personalizado'), {
            'fields': ('custom_css',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return not ComingSoonConfig.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if not change and ComingSoonConfig.objects.exists():
            self.message_user(
                request,
                _("Apenas uma configuração de Coming Soon é permitida. Edite a existente."),
                messages.WARNING
            )
            return
        super().save_model(request, obj, form, change)


@admin.register(ServicePrice)
class ServicePriceAdmin(BaseModelAdmin):
    list_display = ('servico', 'preco')


@admin.register(ActiveAdenaExchangeItem)
class ActiveAdenaExchangeItemAdmin(BaseModelAdmin):
    list_display = ('item_type', 'value_item', 'active', 'created_at')
    list_filter = ('active',)
    search_fields = ('item_type',)


@admin.register(Apoiador)
class ApoiadorAdmin(BaseModelAdmin):
    list_display = ('nome_publico', 'user', 'ativo')
    search_fields = ('nome_publico', 'user__username')


@admin.register(Comissao)
class ComissaoAdmin(BaseModelAdmin):
    # Exibir colunas no list display
    list_display = ('apoiador', 'compra', 'valor', 'pago', 'data_pagamento')
    # Filtros para facilitar a busca no admin
    list_filter = ('pago', 'apoiador', 'data_pagamento')
    # Adicionar campos de pesquisa no admin
    search_fields = ('apoiador__nome_publico', 'compra__user__username')
    # Formulários personalizados no admin
    readonly_fields = ('data_pagamento',)

    # Definir campos editáveis
    fields = ('apoiador', 'compra', 'valor', 'pago', 'data_pagamento')

    # Mostrar o campo de data de pagamento se já for pago
    def save_model(self, request, obj, form, change):
        if obj.pago and not obj.data_pagamento:
            obj.data_pagamento = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ApoiadorDefault)
class ApoiadorDefaultAdmin(BaseModelAdmin):
    list_display = ("id", "ordem", "imagem")
    ordering = ("ordem",)


@admin.register(ManagedLineageAccount)
class ManagedLineageAccountAdmin(BaseModelAdmin):
    list_display = (
        "account_login",
        "manager_user",
        "role",
        "status",
        "created_by",
        "notes",
        "created_at",
    )
    list_filter = ("role", "status", "created_at")
    search_fields = ("account_login", "manager_user__username", "created_by__username", "notes")
    list_editable = ("status",)  # Permite editar o status diretamente na lista
    readonly_fields = ("created_at", "updated_at")
    
    fieldsets = (
        ("Informações da Conta", {
            "fields": ("account_login", "manager_user", "role", "status")
        }),
        ("Delegação", {
            "fields": ("created_by", "notes")
        }),
        ("Datas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )


@admin.register(AccountLinkSlot)
class AccountLinkSlotAdmin(BaseModelAdmin):
    list_display = (
        "user",
        "slots_purchased",
        "purchase_price",
        "purchase_date",
        "created_at",
    )
    list_filter = ("purchase_date", "created_at")
    search_fields = ("user__username", "user__email", "notes")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "purchase_date"
    
    fieldsets = (
        ("Informações da Compra", {
            "fields": ("user", "slots_purchased", "purchase_price")
        }),
        ("Observações", {
            "fields": ("notes",),
            "classes": ("collapse",)
        }),
        ("Datas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    
    def get_queryset(self, request):
        """Otimiza a query incluindo o user"""
        qs = super().get_queryset(request)
        return qs.select_related("user")


class ItemInflationSnapshotDetailInline(admin.TabularInline):
    model = ItemInflationSnapshotDetail
    extra = 0
    readonly_fields = ('item_id', 'item_name', 'location', 'quantity', 'instances', 'unique_owners', 'category')
    can_delete = False
    fields = ('item_id', 'item_name', 'location', 'quantity', 'instances', 'unique_owners', 'category')
    show_change_link = False


@admin.register(ItemInflationCategory)
class ItemInflationCategoryAdmin(BaseModelAdmin):
    list_display = ('name', 'order', 'color', 'item_count')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    filter_horizontal = ()
    
    def item_count(self, obj):
        return len(obj.item_ids) if obj.item_ids else 0
    item_count.short_description = _('Item Count')


@admin.register(ItemInflationSnapshot)
class ItemInflationSnapshotAdmin(BaseModelAdmin):
    list_display = ('snapshot_date', 'total_characters', 'total_items_instances', 'total_items_quantity', 'created_at')
    list_filter = ('snapshot_date', 'created_at')
    search_fields = ('notes',)
    readonly_fields = ('snapshot_date', 'total_characters', 'total_items_instances', 'total_items_quantity', 'created_at', 'updated_at')
    date_hierarchy = 'snapshot_date'
    inlines = [ItemInflationSnapshotDetailInline]
    
    fieldsets = (
        (_('Informações do Snapshot'), {
            'fields': ('snapshot_date', 'total_characters', 'total_items_instances', 'total_items_quantity')
        }),
        (_('Observações'), {
            'fields': ('notes',)
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ItemInflationSnapshotDetail)
class ItemInflationSnapshotDetailAdmin(BaseModelAdmin):
    list_display = ('snapshot', 'item_id', 'item_name', 'location', 'quantity', 'instances', 'unique_owners', 'category')
    list_filter = ('snapshot', 'location', 'category')
    search_fields = ('item_name', 'item_id')
    readonly_fields = ('snapshot', 'item_id', 'item_name', 'location', 'quantity', 'instances', 'unique_owners', 'category', 'created_at', 'updated_at')


@admin.register(ItemInflationStats)
class ItemInflationStatsAdmin(BaseModelAdmin):
    list_display = ('item_id', 'item_name', 'location', 'current_quantity', 'previous_quantity', 'quantity_change', 'change_percentage', 'calculated_at')
    list_filter = ('location', 'category', 'calculated_at')
    search_fields = ('item_name', 'item_id')
    readonly_fields = ('item_id', 'item_name', 'location', 'current_quantity', 'previous_quantity', 'quantity_change', 'change_percentage', 'calculated_at', 'created_at', 'updated_at')


@admin.register(CustomTop)
class CustomTopAdmin(BaseModelAdmin):
    list_display = ('title', 'slug', 'column_label', 'order', 'active')
    list_filter = ('active',)
    search_fields = ('title', 'slug', 'column_label')
    list_editable = ('order', 'active')
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        (_('Informações'), {
            'fields': ('title', 'slug', 'order', 'active')
        }),
        (_('Coluna extra'), {
            'fields': ('column_sql', 'column_label'),
            'description': _(
                'O SQL deve ser uma expressão SELECT válida (subquery, coluna ou função). '
                'Use C para characters, CS para character_subclasses, D para clan_subpledges. '
                'Ex: (SELECT COUNT(*) FROM items WHERE owner_id = C.obj_Id) AS total_items'
            )
        }),
    )


@admin.register(ItemInflationFavorite)
class ItemInflationFavoriteAdmin(BaseModelAdmin):
    list_display = ('user', 'item_id', 'item_name', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'item_name', 'item_id', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (_('Informações do Item'), {
            'fields': ('user', 'item_id', 'item_name')
        }),
        (_('Observações'), {
            'fields': ('notes',)
        }),
        (_('Datas'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )