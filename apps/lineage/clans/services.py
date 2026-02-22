"""
Clans app services - usa LineageClans do query module para acesso ao banco L2.
"""
from utils.dynamic_import import get_query_class


def get_user_lead_clans(account_logins):
    """Retorna clãs onde algum personagem das contas é líder."""
    LineageClans = get_query_class("LineageClans")
    if not LineageClans:
        return []
    return LineageClans.get_user_lead_clans(account_logins)


def _normalize_char_id(char):
    """Garante char_id preenchido - diferentes módulos/DBs usam obj_Id, obj_id, charId, etc."""
    cid = char.get('char_id') or char.get('obj_Id') or char.get('obj_id') or char.get('charId')
    return cid


def get_user_characters(account_logins):
    """Retorna personagens das contas (com char_id normalizado para compatibilidade)."""
    LineageClans = get_query_class("LineageClans")
    if not LineageClans:
        return []
    chars = LineageClans.get_user_characters(account_logins)
    for c in chars:
        if c.get('char_id') is None:
            c['char_id'] = _normalize_char_id(c)
    return chars


def get_clan_basic_info(clan_id):
    """Retorna info básica do clã (clan_id, clan_name, clan_level)."""
    LineageClans = get_query_class("LineageClans")
    if not LineageClans:
        return None
    return LineageClans.get_clan_basic_info(clan_id)


def get_clan_full_details(clan_id):
    """Retorna detalhes completos do clã (leader_name, member_count, reputation, level)."""
    LineageClans = get_query_class("LineageClans")
    if not LineageClans:
        return None
    return LineageClans.get_clan_full_details(clan_id)


def get_top_clans(limit=10):
    """Retorna o top N clãs do servidor (banco L2)."""
    LineageStats = get_query_class("LineageStats")
    if not LineageStats:
        return []
    try:
        result = LineageStats.top_clans(limit=limit)
        return result if result else []
    except Exception:
        return []
