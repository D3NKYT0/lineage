from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel
from .choices import *


class Inventory(BaseModel):
    user = models.ForeignKey(User, related_name='inventories', on_delete=models.CASCADE, verbose_name=_("User"))
    account_name = models.CharField(max_length=100, verbose_name=_("Account Name"))
    character_name = models.CharField(max_length=100, verbose_name=_("Character Name"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        unique_together = ('user', 'character_name')
        verbose_name = _("Inventory")
        verbose_name_plural = _("Inventories")

    def __str__(self):
        return f"{self.character_name} ({self.account_name})"


class InventoryItem(BaseModel):
    inventory = models.ForeignKey(Inventory, related_name='items', on_delete=models.CASCADE, verbose_name=_("Inventory"))
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Quantity"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    added_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Added At"))

    class Meta:
        unique_together = ('inventory', 'item_id', 'enchant')
        verbose_name = _("Inventory Item")
        verbose_name_plural = _("Inventory Items")

    def __str__(self):
        return f"{self.item_name} +{self.enchant} x{self.quantity}"


class BlockedServerItem(BaseModel):
    item_id = models.PositiveIntegerField(unique=True, help_text=_("ID of the blocked item"), verbose_name=_("Item ID"))
    reason = models.CharField(max_length=255, blank=True, help_text=_("Reason for blocking (optional)"), verbose_name=_("Reason"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        verbose_name = _("Blocked Item for Withdrawal")
        verbose_name_plural = _("Blocked Items for Withdrawal")

    def __str__(self):
        return f"Item ID: {self.item_id} - {self.reason if self.reason else _('No specific reason')}"


class CustomItem(BaseModel):
    item_id = models.PositiveIntegerField(unique=True, verbose_name=_("Item ID"))
    nome = models.CharField(max_length=255, unique=True, verbose_name=_("Item Name"))
    imagem = models.ImageField(upload_to='itens_customizados/', null=True, blank=True, verbose_name=_("Image"))

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _("Custom Item")
        verbose_name_plural = _("Custom Items")


class InventoryLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs_inventario', verbose_name=_("User"))
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='logs', verbose_name=_("Inventory"))
    item_id = models.IntegerField(verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=100, verbose_name=_("Item Name"))
    enchant = models.IntegerField(default=0, verbose_name=_("Enchant Level"))
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    acao = models.CharField(max_length=30, choices=ACOES, verbose_name=_("Action"))
    origem = models.CharField(max_length=100, blank=True, null=True, help_text=_("Origin character or user"), verbose_name=_("Origin"))
    destino = models.CharField(max_length=100, blank=True, null=True, help_text=_("Destination character or user"), verbose_name=_("Destination"))
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name=_("Timestamp"))

    def __str__(self):
        return f"{self.get_acao_display()} - {self.item_name} x{self.quantity} ({self.timestamp})"

    class Meta:
        verbose_name = _("Inventory Log")
        verbose_name_plural = _("Inventory Logs")
