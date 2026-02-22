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


def get_user_characters(account_logins):
    """Retorna personagens das contas."""
    LineageClans = get_query_class("LineageClans")
    if not LineageClans:
        return []
    return LineageClans.get_user_characters(account_logins)


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
