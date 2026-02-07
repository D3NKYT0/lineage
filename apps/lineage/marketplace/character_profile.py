"""
Serviço de perfil do personagem no Marketplace.
Monta dados para a página de detalhes: status do L2, inventário, equipamento e linha do tempo.
"""
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime

from utils.dynamic_import import get_query_class
from utils.resources import get_class_name
from apps.lineage.inventory.utils.items import get_itens_json

LineageMarketplace = get_query_class("LineageMarketplace")


def get_character_profile(transfer):
    """
    Monta o perfil completo do personagem para exibição na página de detalhes do marketplace.

    Args:
        transfer: CharacterTransfer (com char_id, char_name, char_level, char_class, listed_at, etc.)

    Returns:
        dict com:
            - char_details: dados do L2 (pvp_kills, pk_count, clan_name, lastAccess, etc.) ou None
            - equipment: lista de itens equipados (PAPERDOLL)
            - inventory: lista de itens do inventário
            - timeline_events: lista de dicts { 'type', 'title', 'description', 'date', 'icon' }
            - has_l2_data: bool (se conseguiu falar com o banco L2)
    """
    result = {
        'char_details': None,
        'equipment': [],
        'inventory': [],
        'timeline_events': [],
        'has_l2_data': False,
    }

    # Nome da classe para uso em todo o perfil
    class_name = get_class_name(transfer.char_class) if transfer.char_class is not None else '-'

    try:
        char_details = LineageMarketplace.get_character_details(transfer.char_id)
    except Exception:
        char_details = None

    if char_details:
        result['char_details'] = char_details
        result['has_l2_data'] = True

        # Inventário e equipamento (alguns schemas podem não ter get_character_items)
        # Converter para dict mutável: o driver pode retornar RowMapping (read-only)
        try:
            items_data = LineageMarketplace.get_character_items(transfer.char_id)
            if isinstance(items_data, dict):
                result['equipment'] = [dict(row) for row in items_data.get('equipment', [])]
                result['inventory'] = [dict(row) for row in items_data.get('inventory', [])]
        except Exception:
            pass

    # Enriquecer equipamento e inventário com nomes (itens.json + CustomItem), mesmo sem L2
    itens_nomes = {}
    try:
        itens_nomes = get_itens_json()
    except Exception:
        pass
    for item in result['equipment'] + result['inventory']:
        raw_id = item.get('item_id') or item.get('item_type')
        if raw_id is None:
            continue
        try:
            item_id_int = int(float(raw_id))
            key = str(item_id_int)
            name_from_json = itens_nomes.get(key)
            if name_from_json is not None and len(name_from_json) > 0 and (name_from_json[0] or "").strip():
                item['item_name'] = (name_from_json[0] or "").strip()
            elif not item.get('item_name') or (str(item.get('item_name', '')).strip() in ('', 'Item Desconhecido', 'Desconhecido')):
                item['item_name'] = _(f"(não identificado - {item_id_int})")
        except (TypeError, ValueError):
            if not item.get('item_name'):
                item['item_name'] = _(f"(não identificado - {raw_id})")

    # Formatar último acesso (Unix timestamp -> string) antes de usar
    last_access_formatted = None
    _la = char_details.get('lastAccess') if char_details else None
    if _la is not None:
        try:
            if isinstance(_la, (int, float)):
                last_access_formatted = datetime.utcfromtimestamp(int(_la)).strftime('%d/%m/%Y %H:%M')
            else:
                last_access_formatted = _la.strftime('%d/%m/%Y %H:%M') if hasattr(_la, 'strftime') else str(_la)
        except (TypeError, ValueError, OSError):
            pass

    # Enriquecer transfer com dados do L2 para o template (evitar quebrar quando DB está off)
    transfer.class_name = class_name
    transfer.pvp_kills = char_details.get('pvp_kills', 0) if char_details else 0
    transfer.pk_count = char_details.get('pk_count', 0) if char_details else 0
    transfer.clan_name = (char_details.get('clan_name') or '').strip() if char_details else ''
    transfer.last_access = last_access_formatted or (char_details.get('lastAccess') if char_details else None)
    transfer.online = char_details.get('online', 0) if char_details else 0

    # Construir linha do tempo (eventos ordenados do mais antigo/conceitual ao mais recente)
    timeline = []

    # 1) Nível e classe (estado atual)
    timeline.append({
        'type': 'level',
        'title': _('Nível {}').format(transfer.char_level),
        'description': _('Classe: {}').format(class_name),
        'date': None,
        'icon': 'fa-level-up-alt',
        'order': 0,
    })

    # 2) Clã (se tiver)
    if result.get('char_details') and (result['char_details'].get('clan_name') or '').strip():
        timeline.append({
            'type': 'clan',
            'title': _('Membro de clã'),
            'description': _('Clã: {}').format(result['char_details'].get('clan_name', '').strip()),
            'date': None,
            'icon': 'fa-users',
            'order': 1,
        })

    # 3) PvP
    pvp = result['char_details'].get('pvp_kills', 0) if result.get('char_details') else 0
    timeline.append({
        'type': 'pvp',
        'title': _('Abates em PvP'),
        'description': _('{} abates em PvP').format(pvp),
        'date': None,
        'icon': 'fa-crosshairs',
        'order': 2,
    })

    # 4) PK
    pk = result['char_details'].get('pk_count', 0) if result.get('char_details') else 0
    timeline.append({
        'type': 'pk',
        'title': _('PK'),
        'description': _('{} PKs').format(pk),
        'date': None,
        'icon': 'fa-skull',
        'order': 3,
    })

    # 5) Último acesso (se já formatamos acima)
    if last_access_formatted:
        timeline.append({
            'type': 'last_access',
            'title': _('Último acesso'),
            'description': last_access_formatted,
            'date': None,
            'icon': 'fa-clock',
            'order': 4,
        })

    # 6) Listado para venda (sempre temos essa data)
    timeline.append({
        'type': 'listed',
        'title': _('Listado para venda'),
        'description': transfer.listed_at.strftime('%d/%m/%Y %H:%M') if transfer.listed_at else '-',
        'date': transfer.listed_at,
        'icon': 'fa-store',
        'order': 5,
    })

    # Ordenar por order
    timeline.sort(key=lambda e: e['order'])

    result['timeline_events'] = timeline
    return result
