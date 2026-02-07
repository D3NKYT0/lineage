from django.shortcuts import render, get_object_or_404
from apps.main.home.decorator import conditional_otp_required
from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.lineage.server.utils.bosses import enrich_raidboss_status
from apps.lineage.server.database import LineageDB
from ..models import ActiveAdenaExchangeItem, CustomTop
from apps.lineage.server.utils.custom_top_sql import validate_custom_top_column_sql

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


@conditional_otp_required
def top_raidboss_view(request):
    db = LineageDB()

    if not db.is_connected():
        bosses = []
    else:
        raw_bosses = LineageStats.raidboss_status()
        bosses = enrich_raidboss_status(raw_bosses)

        dead = [boss for boss in bosses if boss.get('is_alive') is False]
        alive = [boss for boss in bosses if boss.get('is_alive')]
        unknown = [boss for boss in bosses if boss.get('is_alive') not in (True, False)]

        def sort_dead(item):
            respawn = item.get('respawn_seconds')
            return respawn if respawn is not None else float('inf')

        dead.sort(key=sort_dead)
        alive.sort(key=lambda item: item.get('name') or '')
        unknown.sort(key=lambda item: item.get('name') or '')

        bosses = dead + alive + unknown

    context = {
        'bosses': bosses,
        'alive_count': sum(1 for boss in bosses if boss.get('is_alive')),
        'dead_count': sum(1 for boss in bosses if boss.get('is_alive') is False),
    }

    return render(request, 'tops/top_grandboss.html', context)


def _get_lineage_stats_for_custom_top():
    """Retorna LineageStats com top_level_with_extra_column (usa query_default como fallback)."""
    stats = get_query_class("LineageStats")
    if hasattr(stats, 'top_level_with_extra_column'):
        return stats
    from apps.lineage.server.querys.query_default import LineageStats as DefaultStats
    return DefaultStats


@conditional_otp_required
def custom_top_view(request, slug):
    custom_top = get_object_or_404(CustomTop, slug=slug, active=True)
    db = LineageDB()

    if not db.is_connected():
        result = []
    else:
        try:
            validate_custom_top_column_sql(custom_top.column_sql)
            stats = _get_lineage_stats_for_custom_top()
            result = stats.top_level_with_extra_column(
                extra_select_sql=custom_top.column_sql,
                limit=20
            )
            result = attach_crests_to_clans(result)
        except Exception:
            result = []

    context = {
        'players': result,
        'custom_top': custom_top,
        'column_label': custom_top.column_label,
        'column_key': custom_top.get_column_key(),
        'segment': 'top-custom',
        'parent': 'tops',
    }
    return render(request, 'tops/top_custom.html', context)
