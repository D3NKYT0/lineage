from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin


class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 1


@admin.register(Inventory)
class InventoryAdmin(BaseModelAdmin):
    list_display = ('character_name', 'account_name', 'user', 'created_at')
    search_fields = ('character_name', 'account_name', 'user__username')
    inlines = [InventoryItemInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            instance.inventory = form.instance  # FK para Inventory
            instance.save()
        formset.save_m2m()


@admin.register(InventoryItem)
class InventoryItemAdmin(BaseModelAdmin):
    list_display = ('item_name', 'inventory', 'quantity', 'added_at')
    list_filter = ('inventory',)
    search_fields = ('item_name', 'inventory__character_name')


@admin.register(BlockedServerItem)
class BlockedServerItemAdmin(BaseModelAdmin):
    list_display = ('item_id', 'reason', 'created_at')
    search_fields = ('item_id', 'reason')


@admin.register(CustomItem)
class CustomItemAdmin(BaseModelAdmin):
    list_display = ('nome', 'imagem', 'item_id')
    search_fields = ('nome', 'item_id')


@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_name', 'quantity', 'acao', 'origem', 'destino', 'timestamp')
    list_filter = ('acao', 'user', 'origem', 'destino', 'timestamp')
    search_fields = ('user__username', 'item_name', 'acao', 'origem', 'destino')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    fields = ('user', 'inventory', 'item_id', 'item_name', 'enchant', 'quantity', 'acao', 'origem', 'destino', 'timestamp')
    readonly_fields = ('timestamp',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related('user', 'inventory')
