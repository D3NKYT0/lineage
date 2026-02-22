from utils.dynamic_import import get_query_class

def get_user_lead_clans(account_logins):
    """
    Returns a list of clans where any of the provided account's characters is a leader.
    account_logins should be a list of strings (Lineage 2 account logins).
    """
    if not account_logins:
        return []

    LineageDB = get_query_class('LineageDB')
    if not LineageDB:
        return []

    db = LineageDB()
    if not getattr(db, 'enabled', False):
        return []

    # Get schema constants
    import importlib
    import os
    query_module_name = os.getenv('LINEAGE_QUERY_MODULE', 'default')
    try:
        query_module = importlib.import_module(f'apps.lineage.server.querys.query_{query_module_name}')
    except ModuleNotFoundError:
        query_module = importlib.import_module(f'apps.lineage.server.querys.query_default')

    clan_name_source = getattr(query_module, 'CLAN_NAME_SOURCE', 'clan_data')
    char_id_col = getattr(query_module, 'CHAR_ID', 'obj_Id')
    subpledge_filter = getattr(query_module, 'SUBPLEDGE_FILTER', 'type')

    # Build IN clause for account logins
    placeholders = ", ".join([f":acc{i}" for i in range(len(account_logins))])
    params = {f"acc{i}": acc for i, acc in enumerate(account_logins)}

    # Based on the schema type, construct the query
    if clan_name_source == 'clan_data':
        # Name and leader logic is in clan_data
        sql = f"""
            SELECT C.clan_id, C.clan_name, C.clan_level, P.char_name AS leader_name, P.{char_id_col} AS leader_id
            FROM clan_data C
            INNER JOIN characters P ON P.{char_id_col} = C.leader_id
            WHERE P.account_name IN ({placeholders})
        """
    else:
        # Name and leader logic in clan_subpledges (schema varies: sub_pledge_id=0 or type=0)
        sub_filter = "S.sub_pledge_id = 0" if subpledge_filter == 'sub_pledge_id' else "S.type = 0"
        sql = f"""
            SELECT C.clan_id, S.name AS clan_name, C.clan_level, P.char_name AS leader_name, P.{char_id_col} AS leader_id
            FROM clan_data C
            INNER JOIN clan_subpledges S ON S.clan_id = C.clan_id AND {sub_filter}
            INNER JOIN characters P ON P.{char_id_col} = S.leader_id
            WHERE P.account_name IN ({placeholders})
        """

    try:
        result = db.select(sql, params)
        return result if result else []
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching user clans: {e}")
        return []

def get_user_characters(account_logins):
    """
    Returns a list of characters belonging to the provided accounts using the primary LineageServices.find_chars method.
    """
    if not account_logins:
        return []

    from utils.dynamic_import import get_query_class
    LineageServices = get_query_class("LineageServices")
    
    if not LineageServices:
        return []

    all_characters = []
    
    for login in account_logins:
        try:
            personagens = LineageServices.find_chars(login)
            if personagens:
                for char in personagens:
                    all_characters.append({
                        'char_id': char['obj_Id'],
                        'char_name': char['char_name'],
                        'account_name': char.get('account_name', login),
                        'level': char.get('base_level', '-') or 1,
                        'clan_id': char.get('clanid', 0)
                    })
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error fetching user characters for login {login}: {e}")
            
    return all_characters

def get_clan_basic_info(clan_id):
    """
    Retrieves basic info for a specific clan from the game database.
    """
    LineageDB = get_query_class('LineageDB')
    if not LineageDB:
        return None

    db = LineageDB()
    if not getattr(db, 'enabled', False):
        return None

    import importlib
    import os
    query_module_name = os.getenv('LINEAGE_QUERY_MODULE', 'default')
    try:
        query_module = importlib.import_module(f'apps.lineage.server.querys.query_{query_module_name}')
    except ModuleNotFoundError:
        query_module = importlib.import_module(f'apps.lineage.server.querys.query_default')

    clan_name_source = getattr(query_module, 'CLAN_NAME_SOURCE', 'clan_data')
    subpledge_filter = getattr(query_module, 'SUBPLEDGE_FILTER', 'type')

    if clan_name_source == 'clan_data':
        sql = """
            SELECT clan_id, clan_name, clan_level
            FROM clan_data
            WHERE clan_id = :clan_id
        """
    else:
        sub_filter = "S.sub_pledge_id = 0" if subpledge_filter == 'sub_pledge_id' else "S.type = 0"
        sql = f"""
            SELECT C.clan_id, S.name AS clan_name, C.clan_level
            FROM clan_data C
            LEFT JOIN clan_subpledges S ON S.clan_id = C.clan_id AND {sub_filter}
            WHERE C.clan_id = :clan_id
        """

    try:
        result = db.select(sql, {"clan_id": clan_id})
        return result[0] if result else None
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching clan info: {e}")
        return None


def get_clan_full_details(clan_id):
    """
    Retorna detalhes completos do clã (leader_name, member_count, reputation, level).
    Usa get_clan_basic_info para obter clan_name e depois LineageStats.get_clan_details.
    """
    basic = get_clan_basic_info(clan_id)
    if not basic:
        return None
    clan_name = basic.get('clan_name')
    if clan_name:
        try:
            LineageStats = get_query_class("LineageStats")
            if LineageStats:
                full = LineageStats.get_clan_details(clan_name)
                if full:
                    return full
        except Exception:
            pass
    # Fallback: normaliza basic para ter 'level' e campos vazios
    result = dict(basic)
    result['level'] = result.get('level') or result.get('clan_level', '-')
    result.setdefault('leader_name', '')
    result.setdefault('member_count', '-')
    result.setdefault('reputation', '-')
    return result
