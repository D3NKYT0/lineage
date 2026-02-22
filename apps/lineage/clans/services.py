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
        # Name and leader logic usually in clan_subpledges
        sql = f"""
            SELECT C.clan_id, S.name AS clan_name, C.clan_level, P.char_name AS leader_name, P.{char_id_col} AS leader_id
            FROM clan_data C
            INNER JOIN clan_subpledges S ON S.clan_id = C.clan_id AND S.type = '0'
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

    if clan_name_source == 'clan_data':
        sql = """
            SELECT clan_id, clan_name, clan_level
            FROM clan_data
            WHERE clan_id = :clan_id
        """
    else:
        sql = """
            SELECT C.clan_id, S.name AS clan_name, C.clan_level
            FROM clan_data C
            LEFT JOIN clan_subpledges S ON S.clan_id = C.clan_id AND S.type = '0'
            WHERE C.clan_id = :clan_id
        """

    try:
        result = db.select(sql, {"clan_id": clan_id})
        return result[0] if result else None
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching clan info: {e}")
        return None
