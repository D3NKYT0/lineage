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


def get_clan_members(clan_id):
    """Retorna os membros de um clã a partir do banco L2."""
    LineageClans = get_query_class("LineageClans")
    if not LineageClans:
        return []
    
    # Fazemos um fallback suave caso a classe LineageClans antiga não tenha o método ainda
    get_members_func = getattr(LineageClans, 'get_clan_members', None)
    if get_members_func:
        return get_members_func(clan_id)
    
    # Hard fallback apenas como "safety net", logando o aviso
    import logging
    logging.getLogger(__name__).warning("LineageClans.get_clan_members não está implementado na query class atual.")
    from apps.lineage.server.database import LineageDB
    db = LineageDB()
    if getattr(db, 'enabled', False):
        try:
            sql = "SELECT char_name, online FROM characters WHERE clanid = :clan_id OR clan_id = :clan_id ORDER BY online DESC, char_name ASC"
            result = db.select(sql, {"clan_id": clan_id})
            return result if result else []
        except:
            return []
    return []



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
