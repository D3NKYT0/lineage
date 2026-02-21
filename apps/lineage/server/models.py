from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from apps.lineage.server.utils.custom_top_sql import validate_custom_top_column_sql
from django.utils.translation import gettext_lazy as _
from core.models import BaseModel
from apps.main.home.models import User
from apps.lineage.shop.models import ShopPurchase
import os
import uuid


def caminho_imagem_apoiador(instance, filename):
    nome_base, extensao = os.path.splitext(filename)
    novo_nome = f"{slugify(instance.nome_publico)}-{uuid.uuid4().hex[:8]}{extensao}"
    return os.path.join("apoiadores", novo_nome[:95])


class ApiEndpointToggle(BaseModel):
    # =========================== SERVER ENDPOINTS ===========================
    players_online = models.BooleanField(default=True, verbose_name=_("Players Online"))
    top_pvp = models.BooleanField(default=True, verbose_name=_("Top PvP"))
    top_pk = models.BooleanField(default=True, verbose_name=_("Top PK"))
    top_clan = models.BooleanField(default=True, verbose_name=_("Top Clan"))
    top_rich = models.BooleanField(default=True, verbose_name=_("Top Rich"))
    top_online = models.BooleanField(default=True, verbose_name=_("Top Online"))
    top_level = models.BooleanField(default=True, verbose_name=_("Top Level"))
    olympiad_ranking = models.BooleanField(default=True, verbose_name=_("Olympiad Ranking"))
    olympiad_all_heroes = models.BooleanField(default=True, verbose_name=_("Olympiad All Heroes"))
    olympiad_current_heroes = models.BooleanField(default=True, verbose_name=_("Olympiad Current Heroes"))
    grandboss_status = models.BooleanField(default=True, verbose_name=_("Grand Boss Status"))
    raidboss_status = models.BooleanField(default=True, verbose_name=_("Raid Boss Status"))
    siege = models.BooleanField(default=True, verbose_name=_("Siege"))
    siege_participants = models.BooleanField(default=True, verbose_name=_("Siege Participants"))
    boss_jewel_locations = models.BooleanField(default=True, verbose_name=_("Boss Jewel Locations"))
    
    # =========================== AUTHENTICATION ENDPOINTS ===========================
    auth_login = models.BooleanField(default=True, verbose_name=_("Auth Login"))
    auth_refresh = models.BooleanField(default=True, verbose_name=_("Auth Refresh"))
    auth_logout = models.BooleanField(default=True, verbose_name=_("Auth Logout"))
    
    # =========================== USER ENDPOINTS ===========================
    user_profile = models.BooleanField(default=True, verbose_name=_("User Profile"))
    user_change_password = models.BooleanField(default=True, verbose_name=_("User Change Password"))
    user_dashboard = models.BooleanField(default=True, verbose_name=_("User Dashboard"))
    user_stats = models.BooleanField(default=True, verbose_name=_("User Stats"))
    user_game_data = models.BooleanField(default=True, verbose_name=_("User Game Data"))
    
    # =========================== SEARCH ENDPOINTS ===========================
    search_character = models.BooleanField(default=True, verbose_name=_("Search Character"))
    search_item = models.BooleanField(default=True, verbose_name=_("Search Item"))
    
    # =========================== GAME DATA ENDPOINTS ===========================
    clan_detail = models.BooleanField(default=True, verbose_name=_("Clan Detail"))
    auction_items = models.BooleanField(default=True, verbose_name=_("Auction Items"))
    game_summary = models.BooleanField(default=True, verbose_name=_("Game Summary"))
    game_leaderboard = models.BooleanField(default=True, verbose_name=_("Game Leaderboard"))
    
    # =========================== SERVER STATUS ENDPOINTS ===========================
    server_status = models.BooleanField(default=True, verbose_name=_("Server Status"))
    
    # =========================== API INFO ENDPOINTS ===========================
    api_info = models.BooleanField(default=True, verbose_name=_("API Info"))
    
    # =========================== MONITORING ENDPOINTS ===========================
    health_check = models.BooleanField(default=True, verbose_name=_("Health Check"))
    hourly_metrics = models.BooleanField(default=True, verbose_name=_("Hourly Metrics"))
    daily_metrics = models.BooleanField(default=True, verbose_name=_("Daily Metrics"))
    performance_metrics = models.BooleanField(default=True, verbose_name=_("Performance Metrics"))
    slow_queries = models.BooleanField(default=True, verbose_name=_("Slow Queries"))
    cache_stats = models.BooleanField(default=True, verbose_name=_("Cache Stats"))
    
    # =========================== ADMINISTRATION ENDPOINTS ===========================
    api_config = models.BooleanField(default=True, verbose_name=_("API Config"))
    api_config_panel = models.BooleanField(default=True, verbose_name=_("API Config Panel"))
    admin_dashboard = models.BooleanField(default=True, verbose_name=_("Admin Dashboard (PWA)"))

    class Meta:
        verbose_name = _("API Endpoint Toggle")
        verbose_name_plural = _("API Endpoint Toggles")

    def __str__(self):
        return str(_("API Endpoint Configuration"))
    
    def get_endpoint_categories(self):
        """Retorna os endpoints organizados por categoria"""
        return {
            'server': {
                'players_online': self.players_online,
                'top_pvp': self.top_pvp,
                'top_pk': self.top_pk,
                'top_clan': self.top_clan,
                'top_rich': self.top_rich,
                'top_online': self.top_online,
                'top_level': self.top_level,
                'olympiad_ranking': self.olympiad_ranking,
                'olympiad_all_heroes': self.olympiad_all_heroes,
                'olympiad_current_heroes': self.olympiad_current_heroes,
                'grandboss_status': self.grandboss_status,
                'raidboss_status': self.raidboss_status,
                'siege': self.siege,
                'siege_participants': self.siege_participants,
                'boss_jewel_locations': self.boss_jewel_locations,
            },
            'authentication': {
                'auth_login': self.auth_login,
                'auth_refresh': self.auth_refresh,
                'auth_logout': self.auth_logout,
            },
            'user': {
                'user_profile': self.user_profile,
                'user_change_password': self.user_change_password,
                'user_dashboard': self.user_dashboard,
                'user_stats': self.user_stats,
                'user_game_data': self.user_game_data,
            },
            'search': {
                'search_character': self.search_character,
                'search_item': self.search_item,
            },
            'game_data': {
                'clan_detail': self.clan_detail,
                'auction_items': self.auction_items,
                'game_summary': self.game_summary,
                'game_leaderboard': self.game_leaderboard,
            },
            'server_status': {
                'server_status': self.server_status,
            },
            'api_info': {
                'api_info': self.api_info,
            },
            'monitoring': {
                'health_check': self.health_check,
                'hourly_metrics': self.hourly_metrics,
                'daily_metrics': self.daily_metrics,
                'performance_metrics': self.performance_metrics,
                'slow_queries': self.slow_queries,
                'cache_stats': self.cache_stats,
            },
            'administration': {
                'api_config': self.api_config,
                'api_config_panel': self.api_config_panel,
                'admin_dashboard': self.admin_dashboard,
            }
        }
    
    def get_all_endpoints(self):
        """Retorna todos os endpoints como um dicionário simples"""
        return {
            'players_online': self.players_online,
            'top_pvp': self.top_pvp,
            'top_pk': self.top_pk,
            'top_clan': self.top_clan,
            'top_rich': self.top_rich,
            'top_online': self.top_online,
            'top_level': self.top_level,
            'olympiad_ranking': self.olympiad_ranking,
            'olympiad_all_heroes': self.olympiad_all_heroes,
            'olympiad_current_heroes': self.olympiad_current_heroes,
            'grandboss_status': self.grandboss_status,
            'raidboss_status': self.raidboss_status,
            'siege': self.siege,
            'siege_participants': self.siege_participants,
            'boss_jewel_locations': self.boss_jewel_locations,
            'auth_login': self.auth_login,
            'auth_refresh': self.auth_refresh,
            'auth_logout': self.auth_logout,
            'user_profile': self.user_profile,
            'user_change_password': self.user_change_password,
            'user_dashboard': self.user_dashboard,
            'user_stats': self.user_stats,
            'user_game_data': self.user_game_data,
            'search_character': self.search_character,
            'search_item': self.search_item,
            'clan_detail': self.clan_detail,
            'auction_items': self.auction_items,
            'game_summary': self.game_summary,
            'game_leaderboard': self.game_leaderboard,
            'server_status': self.server_status,
            'api_info': self.api_info,
            'health_check': self.health_check,
            'hourly_metrics': self.hourly_metrics,
            'daily_metrics': self.daily_metrics,
            'performance_metrics': self.performance_metrics,
            'slow_queries': self.slow_queries,
            'cache_stats': self.cache_stats,
            'api_config': self.api_config,
            'api_config_panel': self.api_config_panel,
            'admin_dashboard': self.admin_dashboard,
        }


class IndexConfig(BaseModel):
    nome_servidor = models.CharField(max_length=100, default="Lineage 2 PDL", verbose_name=_("Server Name"))
    descricao_servidor = models.CharField(max_length=255, blank=True, default=_("Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna."), verbose_name=_("Server Description"))
    link_patch = models.URLField(default="https://pdl.denky.dev.br/", verbose_name=_("Patch Link"))
    link_cliente = models.URLField(default="https://pdl.denky.dev.br/", verbose_name=_("Client Link"))
    link_discord = models.URLField(default="https://pdl.denky.dev.br/", verbose_name=_("Discord Link"))
    trailer_video_id = models.CharField(max_length=100, blank=True, default="Mm19W1PKMFQ", verbose_name=_("Trailer Video ID"))
    jogadores_online_texto = models.CharField(max_length=255, blank=True, default=_("jogadores online Agora"), verbose_name=_("Players Online Text"))
    imagem_banner = models.ImageField(upload_to='banners/', blank=True, null=True, verbose_name=_("Banner Image"))

    class Meta:
        verbose_name = _("Index Configuration")
        verbose_name_plural = _("Index Configuration")

    def save(self, *args, **kwargs):
        if not self.pk and IndexConfig.objects.exists():
            raise ValidationError(_("Only one server configuration is allowed."))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome_servidor


class IndexConfigTranslation(BaseModel):
    LANGUAGES = [
        ('pt', _('Português')),
        ('en', _('English')),
        ('es', _('Español')),
    ]

    config = models.ForeignKey(IndexConfig, on_delete=models.CASCADE, related_name='translations', verbose_name=_("Configuration"))
    language = models.CharField(max_length=5, choices=LANGUAGES, verbose_name=_("Language"))
    nome_servidor = models.CharField(max_length=100, verbose_name=_("Server Name"))
    descricao_servidor = models.CharField(max_length=255, blank=True, verbose_name=_("Server Description"))
    jogadores_online_texto = models.CharField(max_length=255, blank=True, verbose_name=_("Players Online Text"))

    class Meta:
        unique_together = ('config', 'language')
        verbose_name = _("Index Configuration Translation")
        verbose_name_plural = _("Index Configuration Translations")

    def __str__(self):
        return f"{self.nome_servidor} ({self.language})"


class ComingSoonConfig(BaseModel):
    """Configuração da página Coming Soon (substitui a index quando ativa)."""
    is_active = models.BooleanField(
        default=False,
        verbose_name=_("Ativo"),
        help_text=_("Quando ativo, a página inicial exibe a tela Coming Soon em vez do conteúdo normal.")
    )
    staff_only_login = models.BooleanField(
        default=False,
        verbose_name=_("Apenas staff pode fazer login"),
        help_text=_("Quando ativo junto com a contagem, somente usuários staff (equipe) podem fazer login. Usuários comuns verão mensagem de bloqueio.")
    )
    title = models.CharField(
        max_length=200,
        default=_("Em Breve"),
        verbose_name=_("Título principal")
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        default=_("Algo incrível está por vir. Fique ligado!"),
        verbose_name=_("Subtítulo")
    )
    countdown_date = models.DateTimeField(
        verbose_name=_("Data e hora da contagem regressiva"),
        help_text=_("Data/hora alvo para a contagem regressiva (ex: lançamento do servidor).")
    )
    background_image = models.ImageField(
        upload_to='coming_soon/',
        blank=True,
        null=True,
        verbose_name=_("Imagem de fundo"),
        help_text=_("Imagem de fundo da página. Deixe em branco para usar gradiente padrão.")
    )
    overlay_opacity = models.FloatField(
        default=0.6,
        verbose_name=_("Opacidade do overlay"),
        help_text=_("0 = transparente, 1 = totalmente escuro. Recomendado: 0.4 a 0.7.")
    )
    primary_color = models.CharField(
        max_length=20,
        default="#00d9ff",
        verbose_name=_("Cor primária (hex)"),
        help_text=_("Cor de destaque (título, números, bordas). Ex: #00d9ff")
    )
    secondary_color = models.CharField(
        max_length=20,
        default="#e83e8c",
        verbose_name=_("Cor secundária (hex)"),
        help_text=_("Cor de apoio (brilhos, efeitos). Ex: #e83e8c")
    )
    show_seconds = models.BooleanField(
        default=True,
        verbose_name=_("Mostrar segundos na contagem")
    )
    custom_css = models.TextField(
        blank=True,
        verbose_name=_("CSS personalizado"),
        help_text=_("CSS extra (opcional) para sobrescrever estilos.")
    )

    class Meta:
        verbose_name = _("Coming Soon")
        verbose_name_plural = _("Coming Soon")

    def save(self, *args, **kwargs):
        if not self.pk and ComingSoonConfig.objects.exists():
            raise ValidationError(_("Apenas uma configuração de Coming Soon é permitida."))
        super().save(*args, **kwargs)

    def __str__(self):
        return _("Coming Soon") + (" (ativo)" if self.is_active else " (inativo)")


class ServicePrice(BaseModel):
    SERVICO_CHOICES = [
        ('CHANGE_NICKNAME', _('Change Nickname')),
        ('CHANGE_SEX', _('Change Gender')),
    ]

    servico = models.CharField(max_length=30, choices=SERVICO_CHOICES, unique=True, verbose_name=_("Service"))
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=10.00, verbose_name=_("Price"))

    def __str__(self):
        return f"{self.get_servico_display()} - R${self.preco}"

    @classmethod
    def create_default(cls):
        if not cls.objects.exists():
            cls.objects.create(servico='CHANGE_NICKNAME', preco=10.00)
            cls.objects.create(servico='CHANGE_SEX', preco=10.00)

    class Meta:
        verbose_name = _("Service Price")
        verbose_name_plural = _("Service Prices")


class ActiveAdenaExchangeItem(BaseModel):
    item_type = models.PositiveIntegerField(verbose_name=_("Item ID"), help_text=_("ID of the item used for Adena exchange"))
    value_item = models.PositiveIntegerField(default=1_000_000, verbose_name=_("Adena Value"), help_text=_("Amount of Adena each item represents"))
    active = models.BooleanField(default=False, verbose_name=_("Active"), help_text=_("Mark as active to be used in calculation"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Active Adena Exchange Item")
        verbose_name_plural = _("Active Adena Exchange Items")

    def __str__(self):
        status = _("Active") if self.active else _("Inactive")
        return f"{_('Item')} {self.item_type} - {status}"


class Apoiador(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_("User"))
    nome_publico = models.CharField(max_length=100, verbose_name=_("Public Name"))
    descricao = models.TextField(blank=True, verbose_name=_("Description"))
    link_twitch = models.URLField(blank=True, verbose_name=_("Twitch Link"))
    link_youtube = models.URLField(blank=True, verbose_name=_("YouTube Link"))
    imagem = models.ImageField(upload_to=caminho_imagem_apoiador, null=True, blank=True, verbose_name=_("Image"))
    ativo = models.BooleanField(default=True, verbose_name=_("Active"))

    STATUS_CHOICES = [
        ('pendente', _('Pending')),
        ('aprovado', _('Approved')),
        ('rejeitado', _('Rejected')),
        ('expirado', _('Expired')),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name=_("Status"))

    class Meta:
        verbose_name = _("Supporter")
        verbose_name_plural = _("Supporters")

    def __str__(self):
        return self.nome_publico


class Comissao(BaseModel):
    apoiador = models.ForeignKey(Apoiador, on_delete=models.CASCADE, verbose_name=_("Supporter"))
    compra = models.ForeignKey(ShopPurchase, on_delete=models.CASCADE, verbose_name=_("Shop Purchase"))
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Value"))
    data_pagamento = models.DateTimeField(auto_now_add=True, verbose_name=_("Payment Date"))
    pago = models.BooleanField(default=False, verbose_name=_("Paid"))

    class Meta:
        verbose_name = _("Commission")
        verbose_name_plural = _("Commissions")

    def __str__(self):
        return f"{_('Commission from')} {self.apoiador.nome_publico} - R${self.valor}"


class ApoiadorDefault(BaseModel):
    imagem = models.ImageField(upload_to="apoiadores/default/", verbose_name=_("Imagem Default"))
    ordem = models.PositiveIntegerField(default=0, verbose_name=_("Ordem"))

    class Meta:
        verbose_name = _("Imagem Default de Apoiador")
        verbose_name_plural = _("Imagens Default de Apoiador")
        ordering = ["ordem"]

    def __str__(self):
        return f"Imagem Default #{self.pk}"


class ManagedLineageAccount(BaseModel):
    class Role(models.TextChoices):
        OWNER = 'owner', _('Proprietário')
        CONTRA_MESTRE = 'contra_mestre', _('Contra Mestre')
        VIEWER = 'viewer', _('Visualizador')

    class Status(models.TextChoices):
        PENDING = 'pending', _('Pendente')
        ACTIVE = 'active', _('Ativo')
        REVOKED = 'revoked', _('Revogado')

    account_login = models.CharField(max_length=64, verbose_name=_("Login da Conta"))
    manager_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_lineage_accounts',
        verbose_name=_("Usuário Gestor")
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delegated_lineage_accounts',
        verbose_name=_("Delegado por")
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CONTRA_MESTRE,
        verbose_name=_("Papel")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        verbose_name=_("Status")
    )
    notes = models.CharField(max_length=255, blank=True, verbose_name=_("Observações"))

    class Meta:
        verbose_name = _("Conta Delegada do Lineage")
        verbose_name_plural = _("Contas Delegadas do Lineage")
        unique_together = [('account_login', 'manager_user')]
        ordering = ['account_login']

    def __str__(self):
        return f"{self.account_login} → {self.manager_user.username}"


class AccountLinkSlot(BaseModel):
    """
    Armazena slots de vinculação de contas comprados pelos usuários.
    Cada slot permite vincular uma conta adicional ao UUID do usuário.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='link_slots',
        verbose_name=_("Usuário")
    )
    slots_purchased = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Slots Comprados")
    )
    purchase_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Data da Compra")
    )
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name=_("Preço Pago")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Observações")
    )

    class Meta:
        verbose_name = _("Slot de Vinculação")
        verbose_name_plural = _("Slots de Vinculação")
        ordering = ['-purchase_date']

    def __str__(self):
        return f"{self.user.username} - {self.slots_purchased} slot(s) - {self.purchase_date.strftime('%d/%m/%Y')}"


class ItemInflationCategory(BaseModel):
    """
    Categorias de itens para análise de inflação.
    """
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Category Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    item_ids = models.JSONField(
        default=list,
        help_text=_("List of item IDs that belong to this category"),
        verbose_name=_("Item IDs")
    )
    color = models.CharField(
        max_length=7,
        default="#000000",
        help_text=_("Hex color code for visualization"),
        verbose_name=_("Color")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))

    class Meta:
        verbose_name = _("Item Inflation Category")
        verbose_name_plural = _("Item Inflation Categories")
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class ItemInflationSnapshot(BaseModel):
    """
    Snapshot diário da quantidade de itens no servidor.
    Armazena o estado dos itens em um momento específico para comparação.
    """
    snapshot_date = models.DateField(unique=True, verbose_name=_("Snapshot Date"))
    total_characters = models.PositiveIntegerField(default=0, verbose_name=_("Total Characters"))
    total_items_instances = models.PositiveIntegerField(default=0, verbose_name=_("Total Item Instances"))
    total_items_quantity = models.BigIntegerField(default=0, verbose_name=_("Total Items Quantity"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        verbose_name = _("Item Inflation Snapshot")
        verbose_name_plural = _("Item Inflation Snapshots")
        ordering = ['-snapshot_date']

    def __str__(self):
        return f"Snapshot {self.snapshot_date} - {self.total_items_quantity:,} items"


class ItemInflationSnapshotDetail(BaseModel):
    """
    Detalhes de um snapshot - quantidade de cada item em cada localização.
    """
    snapshot = models.ForeignKey(
        ItemInflationSnapshot,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name=_("Snapshot")
    )
    item_id = models.PositiveIntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=255, blank=True, verbose_name=_("Item Name"))
    location = models.CharField(
        max_length=20,
        choices=[
            ('INVENTORY', _('Inventory')),
            ('WAREHOUSE', _('Warehouse')),
            ('PAPERDOLL', _('Equipped')),
            ('CLANWH', _('Clan Warehouse')),
            ('SITE', _('Site Inventory')),
        ],
        verbose_name=_("Location")
    )
    quantity = models.BigIntegerField(default=0, verbose_name=_("Quantity"))
    instances = models.PositiveIntegerField(default=0, verbose_name=_("Instances"))
    unique_owners = models.PositiveIntegerField(default=0, verbose_name=_("Unique Owners"))
    category = models.ForeignKey(
        ItemInflationCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='snapshot_details',
        verbose_name=_("Category")
    )

    class Meta:
        verbose_name = _("Item Inflation Snapshot Detail")
        verbose_name_plural = _("Item Inflation Snapshot Details")
        unique_together = ['snapshot', 'item_id', 'location']
        ordering = ['-quantity']
        indexes = [
            models.Index(fields=['snapshot', 'item_id']),
            models.Index(fields=['snapshot', 'location']),
            models.Index(fields=['snapshot', 'category']),
        ]

    def __str__(self):
        return f"{self.item_name or f'Item {self.item_id}'} - {self.location} - {self.quantity:,}"


class ItemInflationStats(BaseModel):
    """
    Estatísticas agregadas de inflação de itens.
    Calcula variações entre snapshots.
    """
    item_id = models.PositiveIntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=255, blank=True, verbose_name=_("Item Name"))
    location = models.CharField(
        max_length=20,
        choices=[
            ('INVENTORY', _('Inventory')),
            ('WAREHOUSE', _('Warehouse')),
            ('PAPERDOLL', _('Equipped')),
            ('CLANWH', _('Clan Warehouse')),
            ('SITE', _('Site Inventory')),
        ],
        verbose_name=_("Location")
    )
    current_quantity = models.BigIntegerField(default=0, verbose_name=_("Current Quantity"))
    previous_quantity = models.BigIntegerField(default=0, verbose_name=_("Previous Quantity"))
    quantity_change = models.BigIntegerField(default=0, verbose_name=_("Quantity Change"))
    change_percentage = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Change Percentage")
    )
    calculated_at = models.DateTimeField(auto_now=True, verbose_name=_("Calculated At"))
    category = models.ForeignKey(
        ItemInflationCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stats',
        verbose_name=_("Category")
    )

    class Meta:
        verbose_name = _("Item Inflation Statistic")
        verbose_name_plural = _("Item Inflation Statistics")
        unique_together = ['item_id', 'location']
        ordering = ['-quantity_change']
        indexes = [
            models.Index(fields=['item_id', 'location']),
            models.Index(fields=['location']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        change_sign = "+" if self.quantity_change >= 0 else ""
        return f"{self.item_name or f'Item {self.item_id}'} - {self.location}: {change_sign}{self.quantity_change:,} ({self.change_percentage}%)"


class ItemInflationFavorite(BaseModel):
    """
    Itens favoritos que o usuário quer acompanhar.
    Permite monitorar a quantidade de itens específicos no servidor.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='inflation_favorites',
        verbose_name=_("User")
    )
    item_id = models.PositiveIntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=255, blank=True, verbose_name=_("Item Name"))
    notes = models.TextField(blank=True, verbose_name=_("Notes"), help_text=_("Notas pessoais sobre este item"))

    class Meta:
        verbose_name = _("Item Inflation Favorite")
        verbose_name_plural = _("Item Inflation Favorites")
        unique_together = ['user', 'item_id']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'item_id']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.item_name or f'Item {self.item_id}'}"


class CustomTop(BaseModel):
    """
    Top customizado baseado no Top Level, com coluna extra definida via SQL.
    Permite ao admin criar rankings personalizados adicionando uma nova coluna.
    """
    title = models.CharField(max_length=100, verbose_name=_("Título"))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_("Slug"))
    column_sql = models.TextField(
        verbose_name=_("SQL da coluna extra"),
        validators=[validate_custom_top_column_sql],
        help_text=_(
            "Expressão SQL para a coluna extra. Ex: (SELECT COUNT(*) FROM items WHERE owner_id = C.obj_Id) AS total_items. "
            "Use C para characters, CS para character_subclasses. Apenas SELECT, sem ; ou DDL/DML."
        )
    )
    column_label = models.CharField(
        max_length=80,
        verbose_name=_("Rótulo da coluna"),
        help_text=_("Nome exibido no cabeçalho da tabela")
    )
    order = models.PositiveIntegerField(default=0, verbose_name=_("Ordem"))
    active = models.BooleanField(default=True, verbose_name=_("Ativo"))

    class Meta:
        verbose_name = _("Top Customizado")
        verbose_name_plural = _("Tops Customizados")
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_column_key(self):
        """Extrai o alias da coluna do SQL (após AS)."""
        import re
        m = re.search(r'\s+AS\s+(\w+)\s*$', self.column_sql, re.IGNORECASE)
        return m.group(1) if m else 'custom_col'