import django_filters
from django_filters import rest_framework as filters
from rest_framework import serializers


class CharacterFilter(filters.FilterSet):
    """Filtros para busca de personagens"""
    name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do personagem (busca parcial)')
    level_min = filters.NumberFilter(field_name='level', lookup_expr='gte', help_text='Nível mínimo')
    level_max = filters.NumberFilter(field_name='level', lookup_expr='lte', help_text='Nível máximo')
    class_name = filters.CharFilter(lookup_expr='iexact', help_text='Classe do personagem')
    clan_name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do clã')
    online = filters.BooleanFilter(help_text='Filtrar apenas personagens online')
    
    class Meta:
        fields = ['name', 'level_min', 'level_max', 'class_name', 'clan_name', 'online']


class ItemFilter(filters.FilterSet):
    """Filtros para busca de itens"""
    name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do item (busca parcial)')
    item_type = filters.CharFilter(lookup_expr='iexact', help_text='Tipo do item')
    grade = filters.CharFilter(lookup_expr='iexact', help_text='Grade do item')
    enchant_min = filters.NumberFilter(field_name='enchant_level', lookup_expr='gte', help_text='Enchant mínimo')
    enchant_max = filters.NumberFilter(field_name='enchant_level', lookup_expr='lte', help_text='Enchant máximo')
    price_min = filters.NumberFilter(field_name='price', lookup_expr='gte', help_text='Preço mínimo')
    price_max = filters.NumberFilter(field_name='price', lookup_expr='lte', help_text='Preço máximo')
    
    class Meta:
        fields = ['name', 'item_type', 'grade', 'enchant_min', 'enchant_max', 'price_min', 'price_max']


class RankingFilter(filters.FilterSet):
    """Filtros para rankings"""
    class_name = filters.CharFilter(lookup_expr='iexact', help_text='Filtrar por classe')
    clan_name = filters.CharFilter(lookup_expr='icontains', help_text='Filtrar por clã')
    level_min = filters.NumberFilter(field_name='level', lookup_expr='gte', help_text='Nível mínimo')
    level_max = filters.NumberFilter(field_name='level', lookup_expr='lte', help_text='Nível máximo')
    
    class Meta:
        fields = ['class_name', 'clan_name', 'level_min', 'level_max']


class AuctionFilter(filters.FilterSet):
    """Filtros para itens do leilão"""
    item_name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do item')
    seller_name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do vendedor')
    price_min = filters.NumberFilter(field_name='current_bid', lookup_expr='gte', help_text='Preço mínimo')
    price_max = filters.NumberFilter(field_name='current_bid', lookup_expr='lte', help_text='Preço máximo')
    ending_soon = filters.BooleanFilter(method='filter_ending_soon', help_text='Itens terminando em breve')
    
    def filter_ending_soon(self, queryset, name, value):
        if value:
            from django.utils import timezone
            from datetime import timedelta
            # Itens que terminam nas próximas 24 horas
            return queryset.filter(end_time__lte=timezone.now() + timedelta(hours=24))
        return queryset
    
    class Meta:
        fields = ['item_name', 'seller_name', 'price_min', 'price_max', 'ending_soon']


class SiegeFilter(filters.FilterSet):
    """Filtros para dados de cerco"""
    castle_name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do castelo')
    is_under_siege = filters.BooleanFilter(help_text='Filtrar apenas cercos ativos')
    owner_clan = filters.CharFilter(lookup_expr='icontains', help_text='Clã proprietário')
    
    class Meta:
        fields = ['castle_name', 'is_under_siege', 'owner_clan']


class BossFilter(filters.FilterSet):
    """Filtros para status de bosses"""
    boss_name = filters.CharFilter(lookup_expr='icontains', help_text='Nome do boss')
    is_alive = filters.BooleanFilter(help_text='Filtrar apenas bosses vivos')
    location = filters.CharFilter(lookup_expr='icontains', help_text='Localização do boss')
    
    class Meta:
        fields = ['boss_name', 'is_alive', 'location'] 