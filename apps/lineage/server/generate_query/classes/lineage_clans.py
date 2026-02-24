"""Template da classe LineageClans - Clãs e Recrutamento Web"""

def get_lineage_clans_template(char_id: str, clan_structure: dict, clan_id_col: str = 'clan_id',
                                clan_leader_col: str = 'leader_id') -> str:
    """
    Gera o código da classe LineageClans.

    Args:
        char_id: Nome da coluna de ID do personagem (obj_Id, charId, char_id)
        clan_structure: Dict com clan_name_source, subpledge_filter
        clan_id_col: Nome da coluna de ID do clan
        clan_leader_col: Nome da coluna de líder (em clan_data)
    """
    clan_name_source = clan_structure.get('clan_name_source', 'clan_data')
    subpledge_filter = clan_structure.get('subpledge_filter', 'sub_pledge_id')
    sub_filter = "S.sub_pledge_id = 0" if subpledge_filter == 'sub_pledge_id' else "S.type = 0"

    if clan_name_source == 'clan_data':
        get_user_lead_clans_sql = f"""
            SELECT C.{clan_id_col}, C.clan_name, C.clan_level, P.char_name AS leader_name, P.{char_id} AS leader_id
            FROM clan_data C
            INNER JOIN characters P ON P.{char_id} = C.{clan_leader_col}
            WHERE P.account_name IN ({{placeholders}})
        """
        get_clan_basic_info_sql = f"""
            SELECT {clan_id_col}, clan_name, clan_level
            FROM clan_data
            WHERE {clan_id_col} = :clan_id
        """
    else:
        get_user_lead_clans_sql = f"""
            SELECT C.{clan_id_col}, S.name AS clan_name, C.clan_level, P.char_name AS leader_name, P.{char_id} AS leader_id
            FROM clan_data C
            INNER JOIN clan_subpledges S ON S.clan_id = C.{clan_id_col} AND {sub_filter}
            INNER JOIN characters P ON P.{char_id} = S.leader_id
            WHERE P.account_name IN ({{placeholders}})
        """
        get_clan_basic_info_sql = f"""
            SELECT C.{clan_id_col}, S.name AS clan_name, C.clan_level
            FROM clan_data C
            LEFT JOIN clan_subpledges S ON S.clan_id = C.{clan_id_col} AND {sub_filter}
            WHERE C.{clan_id_col} = :clan_id
        """

    return f'''class LineageClans:

    @staticmethod
    def get_user_lead_clans(account_logins):
        """Retorna clãs onde algum personagem das contas é líder."""
        if not account_logins:
            return []
        db = LineageDB()
        if not getattr(db, 'enabled', False):
            return []
        placeholders = ", ".join([f":acc{{i}}" for i in range(len(account_logins))])
        params = {{f"acc{{i}}": acc for i, acc in enumerate(account_logins)}}
        sql = f"""
            {get_user_lead_clans_sql.strip()}
        """
        try:
            result = db.select(sql, params)
            return result if result else []
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"LineageClans.get_user_lead_clans: {{e}}")
            return []

    @staticmethod
    def get_user_characters(account_logins):
        """Retorna personagens das contas usando LineageServices.find_chars."""
        if not account_logins:
            return []
        all_characters = []
        for login in account_logins:
            try:
                personagens = LineageServices.find_chars(login)
                if personagens:
                    for char in personagens:
                        all_characters.append({{
                            'char_id': char.get('{char_id}') or char.get('obj_Id') or char.get('obj_id') or char.get('charId'),
                            'char_name': char.get('char_name'),
                            'account_name': char.get('account_name', login),
                            'level': char.get('base_level') or char.get('level', 1),
                            'clan_id': char.get('clanid', 0) or char.get('clan_id', 0)
                        }})
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"LineageClans.get_user_characters: {{e}}")
        return all_characters

    @staticmethod
    def get_clan_basic_info(clan_id):
        """Retorna info básica do clã (clan_id, clan_name, clan_level)."""
        db = LineageDB()
        if not getattr(db, 'enabled', False):
            return None
        sql = """
            {get_clan_basic_info_sql}
        """
        try:
            result = db.select(sql, {{"clan_id": clan_id}})
            return result[0] if result else None
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"LineageClans.get_clan_basic_info: {{e}}")
            return None

    @staticmethod
    def get_clan_full_details(clan_id):
        """Retorna detalhes completos (leader_name, member_count, reputation, level)."""
        basic = LineageClans.get_clan_basic_info(clan_id)
        if not basic:
            return None
        clan_name = basic.get('clan_name')
        if clan_name:
            try:
                full = LineageStats.get_clan_details(clan_name)
                if full:
                    return full
            except Exception:
                pass
        result = dict(basic)
        result['level'] = result.get('level') or result.get('clan_level', '-')
        result.setdefault('leader_name', '')
        result.setdefault('member_count', '-')
        result.setdefault('reputation', '-')
        return result

    @staticmethod
    def get_clan_members(clan_id):
        """Retorna os membros de um clã gerado de forma dinâmica."""
        db = LineageDB()
        if not getattr(db, 'enabled', False):
            return []
        try:
            sql = """
                SELECT 
                    C.char_name, 
                    C.online, 
                    C.pvpkills, 
                    C.pkkills,
                    (SELECT S0.level FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS level,
                    (SELECT S0.class_id FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS base,
                    C.{access_level_col} AS accesslevel
                FROM characters C
                WHERE C.clanid = :clan_id OR C.clan_id = :clan_id
                ORDER BY C.online DESC, level DESC, C.char_name ASC
            """
            result = db.select(sql, {{"clan_id": clan_id}})
            return result if result else []
        except Exception as e:
            try:
                # Fallback mais básico
                sql_fallback = "SELECT char_name, online FROM characters WHERE clanid = :clan_id OR clan_id = :clan_id ORDER BY online DESC, char_name ASC"
                result = db.select(sql_fallback, {{"clan_id": clan_id}})
                return result if result else []
            except:
                return []

'''
