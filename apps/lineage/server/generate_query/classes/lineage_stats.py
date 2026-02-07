"""Template da classe LineageStats - Rankings e Estatísticas"""

def get_lineage_stats_template(char_id: str, access_level: str, has_subclass: bool, 
                                subclass_char_id: str, clan_structure: dict, base_class_col: str = 'classid',
                                clan_id_col: str = 'clan_id', crest_col: str = None, clan_leader_col: str = None,
                                has_raidboss_table: bool = False, raidboss_table_name: str = 'raidboss_spawnlist',
                                raidboss_id_col: str = 'boss_id', raidboss_respawn_col: str = 'respawn_time',
                                has_grandboss_table: bool = False, grandboss_table_name: str = 'grandboss_data',
                                grandboss_id_col: str = 'boss_id', grandboss_respawn_col: str = 'respawn_time',
                                castle_siege_date_col: str = 'siegeDate', castle_treasury_col: str = 'treasury',
                                subclass_filter_base: str = "isBase = '1'", subclass_filter_sub: str = "isBase = '0'") -> str:
    """
    Gera o código da classe LineageStats
    
    Args:
        char_id: Nome da coluna de ID do personagem (obj_Id, charId, char_id)
        access_level: Nome da coluna de access level
        has_subclass: Se tem tabela character_subclasses
        subclass_char_id: Nome da coluna de ID na tabela de subclasses
        clan_structure: Dict com estrutura de clans
        base_class_col: Nome da coluna de classe base (classid, base_class)
        clan_id_col: Nome da coluna de ID do clan (clan_id, clanId, id)
        crest_col: Nome da coluna de crest (crest_id, crestId, crest) ou None se não existir
        clan_leader_col: Nome da coluna de líder do clan (leader_id, leaderId) ou None se não existir
        has_raidboss_table: Se existe tabela de raidboss (raidboss_spawnlist ou raidboss_status)
        raidboss_table_name: Nome da tabela de raidboss (raidboss_spawnlist ou raidboss_status)
        raidboss_id_col: Nome da coluna de ID do raidboss (boss_id, id, npc_id)
        raidboss_respawn_col: Nome da coluna de respawn (respawn_time, respawnTime, respawn)
        has_grandboss_data: Se existe tabela grandboss_data
    """
    
    # Determinar JOIN com clan
    if clan_structure['clan_name_source'] == 'clan_data':
        # clan_name diretamente em clan_data
        clan_join = """
            LEFT JOIN clan_data D ON D.clan_id = C.clanid"""
        clan_name_field = "D.clan_name"
        ally_field = "D.ally_id"
    elif clan_structure['clan_name_source'] == 'clan_subpledges_simple':
        # clan_subpledges sem filtro (tabela simples)
        clan_join = """
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid"""
        clan_name_field = "D.name AS clan_name"
        ally_field = "CD.ally_id"
    else:
        # clan_subpledges com filtro (sub_pledge_id ou type)
        filter_col = clan_structure.get('subpledge_filter', 'sub_pledge_id')
        clan_join = f"""
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.{filter_col} = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid"""
        clan_name_field = "D.name AS clan_name"
        ally_field = "CD.ally_id"
    
    # Subclass JOIN
    subclass_join = ""
    level_source = "C.level"
    class_source = f"C.{base_class_col}"
    
    if has_subclass:
        # Extrair apenas o nome da coluna do filtro (sem CS. e sem o valor)
        filter_col_name = subclass_filter_base.split('=')[0].strip().replace('CS.', '').replace('C.', '')
        filter_value = subclass_filter_base.split('=')[1].strip()
        subclass_join = f"""
            LEFT JOIN character_subclasses CS ON CS.{subclass_char_id} = C.{char_id} AND CS.{filter_col_name} = {filter_value}"""
        level_source = "CS.level"
        class_source = "CS.class_id"
    
    # Construir query de get_crests baseada nas colunas reais
    if crest_col:
        crests_select = f"{clan_id_col}, {crest_col}"
    else:
        # Se não tem coluna de crest, retornar apenas o ID do clan
        crests_select = clan_id_col
    
    # Placeholder para interpolar variável no código gerado
    item_bonus_placeholder = "{" + "item_bonus_sql" + "}"
    
    # Join específico para top_clans (C = clan_data, não characters)
    if clan_structure['clan_name_source'] == 'clan_data':
        top_clans_join = ""
        top_clans_name = "C.clan_name"
    else:
        # Precisa buscar de clan_subpledges
        filter_col = clan_structure.get('subpledge_filter', 'sub_pledge_id')
        top_clans_join = f"""
            LEFT JOIN clan_subpledges S ON S.clan_id = C.clan_id AND S.{filter_col} = 0"""
        top_clans_name = "S.name AS clan_name"
    
    # Join do leader para top_clans
    if clan_leader_col:
        leader_join = f"""
            LEFT JOIN characters P ON P.{char_id} = C.{clan_leader_col}"""
        leader_select = "P.char_name"
    else:
        # Se não tem coluna de leader, buscar via subquery ou deixar NULL
        leader_join = ""
        leader_select = "NULL AS char_name"
    
    # Construir query de get_clan_details baseada na estrutura de clan
    if clan_structure['clan_name_source'] == 'clan_data':
        # clan_name diretamente em clan_data
        if clan_leader_col:
            leader_join_clan = f"LEFT JOIN characters P ON P.{char_id} = C.{clan_leader_col}"
            leader_select_clan = "P.char_name AS leader_name"
        else:
            leader_join_clan = ""
            leader_select_clan = f"(SELECT char_name FROM characters WHERE clanid = C.{clan_id_col} AND {access_level} = '0' LIMIT 1) AS leader_name"
        
        get_clan_details_sql = f'''sql = f"""
            SELECT 
                C.{clan_id_col}, 
                C.clan_name,
                C.clan_level AS level, 
                C.reputation_score AS reputation, 
                C.ally_id,
                (SELECT COUNT(*) FROM characters WHERE clanid = C.{clan_id_col}) AS member_count,
                {leader_select_clan}
            FROM clan_data C
            {leader_join_clan}
            WHERE C.clan_name = :clan_name
            LIMIT 1
        """
        result = LineageStats._run_query(sql, {{"clan_name": clan_name}})
        return result[0] if result and len(result) > 0 else None'''
    else:
        # clan_name em clan_subpledges
        filter_col = clan_structure.get('subpledge_filter', 'sub_pledge_id')
        # Determinar como buscar o leader
        if clan_leader_col:
            if 'leader_id' in clan_leader_col:
                leader_join_clan = f"LEFT JOIN characters P ON P.{char_id} = D.{clan_leader_col.replace('C.', '')}"
                leader_select_clan = "P.char_name AS leader_name"
            elif 'leader_name' in clan_leader_col:
                leader_join_clan = "LEFT JOIN characters P ON P.char_name = D.leader_name"
                leader_select_clan = "P.char_name AS leader_name"
            else:
                leader_join_clan = ""
                leader_select_clan = f"(SELECT char_name FROM characters WHERE clanid = C.{clan_id_col} AND {access_level} = '0' LIMIT 1) AS leader_name"
        else:
            leader_join_clan = ""
            leader_select_clan = f"(SELECT char_name FROM characters WHERE clanid = C.{clan_id_col} AND {access_level} = '0' LIMIT 1) AS leader_name"
        
        get_clan_details_sql = f'''sql = f"""
            SELECT 
                C.{clan_id_col}, 
                D.name AS clan_name,
                C.clan_level AS level, 
                C.reputation_score AS reputation, 
                C.ally_id,
                (SELECT COUNT(*) FROM characters WHERE clanid = C.{clan_id_col}) AS member_count,
                {leader_select_clan}
            FROM clan_data C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.{clan_id_col} AND D.{filter_col} = 0
            {leader_join_clan}
            WHERE D.name = :clan_name
            LIMIT 1
        """
        result = LineageStats._run_query(sql, {{"clan_name": clan_name}})
        return result[0] if result and len(result) > 0 else None'''
    
    return f'''class LineageStats:

    @staticmethod
    def _run_query(sql, params=None, use_cache=True):
        return LineageDB().select(sql, params=params, use_cache=use_cache)
    
    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_crests(ids, type='clan'):
        if not ids:
            return []

        sql = f"""
            SELECT {crests_select}
            FROM clan_data
            WHERE {clan_id_col} IN :ids
        """
        return LineageStats._run_query(sql, {{"ids": tuple(ids)}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def players_online():
        sql = "SELECT COUNT(*) AS quant FROM characters WHERE online > 0 AND {access_level} = '0'"
        return LineageStats._run_query(sql)
    
    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_pvp(limit=10):
        sql = """
            SELECT 
                C.char_name, 
                C.pvpkills, 
                C.pkkills, 
                C.online, 
                C.onlinetime,
                {level_source},
                {class_source} AS base,
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id
            FROM characters C{subclass_join}{clan_join}
            WHERE C.{access_level} = '0'
            ORDER BY pvpkills DESC, pkkills DESC, onlinetime DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_pk(limit=10):
        sql = """
            SELECT 
                C.char_name, 
                C.pvpkills, 
                C.pkkills, 
                C.online, 
                C.onlinetime,
                {level_source},
                {class_source} AS base,
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id
            FROM characters C{subclass_join}{clan_join}
            WHERE C.{access_level} = '0'
            ORDER BY pkkills DESC, pvpkills DESC, onlinetime DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_online(limit=10):
        sql = """
            SELECT 
                C.char_name, 
                C.pvpkills, 
                C.pkkills, 
                C.online, 
                C.onlinetime,
                {level_source},
                {class_source} AS base,
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id
            FROM characters C{subclass_join}{clan_join}
            WHERE C.{access_level} = '0'
            ORDER BY onlinetime DESC, pvpkills DESC, pkkills DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_level(limit=10):
        sql = """
            SELECT 
                C.char_name, 
                C.pvpkills, 
                C.pkkills, 
                C.online, 
                C.onlinetime, 
                {level_source},
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id
            FROM characters C{subclass_join}{clan_join}
            WHERE C.{access_level} = '0'
            ORDER BY {level_source} DESC, C.onlinetime DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_level_with_extra_column(extra_select_sql, limit=20):
        """
        Top Level com coluna extra. O extra_select_sql deve ser validado antes.
        Ex: (SELECT COUNT(*) FROM items WHERE owner_id = C.{char_id}) AS total_items
        """
        sql = f"""
            SELECT 
                C.char_name, 
                C.pvpkills, 
                C.pkkills, 
                C.online, 
                C.onlinetime, 
                {level_source},
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id,
                {{extra_select_sql}}
            FROM characters C{subclass_join}{clan_join}
            WHERE C.{access_level} = '0'
            ORDER BY {level_source} DESC, C.onlinetime DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_adena(limit=10, adn_billion_item=0, value_item=1000000):
        # Otimização: usar LEFT JOIN ao invés de subqueries correlacionadas
        # Isso é muito mais rápido pois permite uso de índices
        bonus_join = ""
        bonus_select = ""
        if adn_billion_item != 0:
            bonus_join = f"""
            LEFT JOIN (
                SELECT owner_id, SUM(count) * :value_item AS bonus_adenas
                FROM items
                WHERE item_id = :adn_billion_item
                GROUP BY owner_id
            ) I2 ON I2.owner_id = C.{char_id}
            """
            bonus_select = "IFNULL(I2.bonus_adenas, 0) +"
        
        sql = f"""
            SELECT 
                C.char_name, 
                C.online, 
                C.onlinetime, 
                {level_source}, 
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id,
                ({bonus_select} IFNULL(I1.adenas, 0)) AS adenas
            FROM characters C{subclass_join}{clan_join}
            LEFT JOIN (
                SELECT owner_id, SUM(count) AS adenas
                FROM items
                WHERE item_id = '57'
                GROUP BY owner_id
            ) I1 ON I1.owner_id = C.{char_id}
            {bonus_join}
            WHERE C.{access_level} = '0'
            ORDER BY adenas DESC, C.onlinetime DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{
            "limit": limit,
            "adn_billion_item": adn_billion_item,
            "value_item": value_item
        }})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_clans(limit=10):
        sql = f"""
            SELECT 
                C.clan_id, 
                {top_clans_name},
                C.clan_level, 
                C.reputation_score, 
                C.ally_id,
                {leader_select}, 
                (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS membros
            FROM clan_data C{top_clans_join}{leader_join}
            ORDER BY C.clan_level DESC, C.reputation_score DESC, membros DESC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_ranking():
        sql = """
            SELECT 
                C.char_name, 
                C.online, 
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id,
                {class_source} AS base, 
                O.olympiad_points
            FROM olympiad_nobles O
            LEFT JOIN characters C ON C.{char_id} = O.char_id{subclass_join}{clan_join}
            ORDER BY olympiad_points DESC, base ASC, char_name ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_all_heroes():
        sql = """
            SELECT 
                C.char_name, 
                C.online, 
                {clan_name_field}, 
                C.clanid AS clan_id,
                {ally_field} AS ally_id,
                {class_source} AS base, 
                H.count
            FROM heroes H
            LEFT JOIN characters C ON C.{char_id} = H.char_id{subclass_join}{clan_join}
            WHERE H.played > 0 AND H.count > 0
            ORDER BY H.count DESC, base ASC, char_name ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_current_heroes():
        sql = """
            SELECT 
                C.char_name, 
                C.online, 
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id,
                {class_source} AS base
            FROM heroes H
            LEFT JOIN characters C ON C.{char_id} = H.char_id{subclass_join}{clan_join}
            WHERE H.played > 0 AND H.count > 0
            ORDER BY base ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def grandboss_status():
        {"return []  # Tabela de grandboss não existe" if not has_grandboss_table else f'''sql = """
            SELECT {grandboss_id_col} AS boss_id, {grandboss_respawn_col} AS respawn
            FROM {grandboss_table_name}
            ORDER BY {grandboss_respawn_col} DESC
        """
        return LineageStats._run_query(sql)'''}

    @staticmethod
    @cache_lineage_result(timeout=300)
    def raidboss_status():
        {"return []  # Tabela de raidboss não existe" if not has_raidboss_table else f'''sql = """
            SELECT 
                B.{raidboss_id_col} AS boss_id,
                B.{raidboss_respawn_col} AS respawn,
                CASE 
                    WHEN B.{raidboss_respawn_col} IS NULL OR B.{raidboss_respawn_col} = 0 THEN 'Alive'
                    WHEN (
                        (B.{raidboss_respawn_col} > 9999999999 AND B.{raidboss_respawn_col} > UNIX_TIMESTAMP() * 1000) OR
                        (B.{raidboss_respawn_col} <= 9999999999 AND B.{raidboss_respawn_col} > UNIX_TIMESTAMP())
                    ) THEN 'Dead'
                    ELSE 'Alive'
                END AS status,
                CASE 
                    WHEN B.{raidboss_respawn_col} IS NULL OR B.{raidboss_respawn_col} = 0 THEN NULL
                    WHEN B.{raidboss_respawn_col} > 9999999999 THEN FROM_UNIXTIME(B.{raidboss_respawn_col} / 1000)
                    ELSE FROM_UNIXTIME(B.{raidboss_respawn_col})
                END AS respawn_human
            FROM {raidboss_table_name} B
            ORDER BY respawn DESC
        """
        return LineageStats._run_query(sql)'''}

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege():
        sql = f"""
            SELECT 
                W.id, 
                W.name, 
                {"W." + castle_siege_date_col + " AS sdate" if castle_siege_date_col else "NULL AS sdate"}, 
                W.{castle_treasury_col} AS stax,
                {leader_select.replace('P.', 'L.')}, 
                {top_clans_name.replace('C.', 'CLAN.')},
                CLAN.clan_id,
                CLAN.ally_id,
                A.ally_name
            FROM castle W
            LEFT JOIN clan_data CLAN ON CLAN.hasCastle = W.id{top_clans_join.replace('C.clan_id', 'CLAN.clan_id')}{leader_join.replace('P.', 'L.').replace('C.', 'CLAN.')}
            LEFT JOIN ally_data A ON A.ally_id = CLAN.ally_id
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def search_characters(query, limit=20):
        """Busca personagens por nome (busca parcial)"""
        sql = """
            SELECT 
                C.{char_id} as char_id,
                C.char_name, 
                {level_source},
                {class_source} AS base,
                C.online,
                C.lastAccess,
                {clan_name_field},
                C.clanid AS clan_id,
                {ally_field} AS ally_id,
                C.x,
                C.y,
                C.z
            FROM characters C{subclass_join}{clan_join}
            WHERE C.{access_level} = '0' 
            AND C.char_name LIKE :query
            ORDER BY {level_source} DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {{"query": "%" + query + "%", "limit": limit}})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_clan_details(clan_name):
        """Busca detalhes de um clã específico por nome"""
        {get_clan_details_sql}

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege_participants(castle_id):
        # TODO: Adaptar dinamicamente para diferentes schemas  
        return []

    @staticmethod
    @cache_lineage_result(timeout=300)
    def boss_jewel_locations(boss_jewel_ids):
        # TODO: Adaptar dinamicamente para diferentes schemas
        return []


'''

