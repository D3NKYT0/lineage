from django.shortcuts import render
from apps.main.home.decorator import conditional_otp_required
from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.lineage.server.database import LineageDB
from ..models import ActiveAdenaExchangeItem

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


@conditional_otp_required
def top_pvp_view(request):
    db = LineageDB()
    result = LineageStats.top_pvp(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_pvp.html', {'players': result})


@conditional_otp_required
def top_pk_view(request):
    db = LineageDB()
    result = LineageStats.top_pk(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_pk.html', {'players': result})


@conditional_otp_required
def top_adena_view(request):
    db = LineageDB()

    adn_billion_item = 0
    value_item = 1000000000

    # Buscar o item ativo
    active_item = ActiveAdenaExchangeItem.objects.filter(active=True).order_by('-created_at').first()
    if active_item:
        adn_billion_item = active_item.item_type
        value_item = active_item.value_item

    if db.is_connected():
        result = LineageStats.top_adena(limit=20, adn_billion_item=adn_billion_item, value_item=value_item)
        result = attach_crests_to_clans(result)
    else:
        result = list()

    return render(request, 'tops/top_adena.html', {'players': result})


@conditional_otp_required
def top_clans_view(request):
    db = LineageDB()
    clanes = LineageStats.top_clans(limit=20) if db.is_connected() else []
    clanes = attach_crests_to_clans(clanes)
    return render(request, 'tops/top_clans.html', {'clans': clanes})


@conditional_otp_required
def top_level_view(request):
    db = LineageDB()
    result = LineageStats.top_level(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_level.html', {'players': result})


def top_online_view(request):
    db = LineageDB()
    result = LineageStats.top_online(limit=20) if db.is_connected() else []
    result = attach_crests_to_clans(result)
    return render(request, 'tops/top_online.html', {"ranking": result})
