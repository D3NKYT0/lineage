"""
Query File: query_mobius.py
Generated automatically by Query Generator
Date: 2025-12-09 19:10:15
Database Schema: mobius

⚠️  Este arquivo foi gerado automaticamente.
    Para regenerar, execute: python gerar_query.py
"""

from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result

import time
import base64
import hashlib
from datetime import datetime


# ============================================================================
# CONFIGURAÇÃO DO SCHEMA - Nomes reais das colunas do banco
# ============================================================================
# ⚠️  NÃO use nomes hardcoded nas views!
#     SEMPRE use estas constantes:
#     
#     Exemplo:
#       ❌ ERRADO: account['accesslevel']
#       ✅ CERTO:  account[ACCESS_LEVEL]

# Tabela: characters
CHAR_ID = 'obj_Id'                    # obj_Id, charId ou char_id
ACCESS_LEVEL = 'access_level'          # accesslevel, accessLevel ou access_level
BASE_CLASS_COL = None      # classid, base_class ou class_id (None se não existe em characters)

# Tabela: character_subclasses
HAS_SUBCLASS = True            # Se tem tabela de subclass
SUBCLASS_CHAR_ID = 'char_obj_id'  # Coluna de ID na subclass

# Estrutura de Clans
CLAN_NAME_SOURCE = 'clan_subpledges'  # clan_data, clan_subpledges ou clan_subpledges_simple
SUBPLEDGE_FILTER = 'type'  # sub_pledge_id, type ou None
HAS_ALLY_DATA = True          # Se tem tabela ally_data

# ============================================================================


class LineageStats:

    @staticmethod
    def _run_query(sql, params=None, use_cache=True):
        return LineageDB().select(sql, params=params, use_cache=use_cache)
    
    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_crests(ids, type='clan'):
        if not ids:
            return []

        sql = f"""
            SELECT clan_id, crest
            FROM clan_data
            WHERE clan_id IN :ids
        """
        return LineageStats._run_query(sql, {"ids": tuple(ids)})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def players_online():
        sql = "SELECT COUNT(*) AS quant FROM characters WHERE online > 0 AND accesslevel = '0'"
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
                CS.level,
                CS.class_id AS base,
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY pvpkills DESC, pkkills DESC, onlinetime DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

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
                CS.level,
                CS.class_id AS base,
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY pkkills DESC, pvpkills DESC, onlinetime DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

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
                CS.level,
                CS.class_id AS base,
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY onlinetime DESC, pvpkills DESC, pkkills DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

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
                CS.level,
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY CS.level DESC, C.onlinetime DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_level_with_extra_column(extra_select_sql, limit=20):
        sql = f"""
            SELECT 
                C.char_name, 
                C.pvpkills, 
                C.pkkills, 
                C.online, 
                C.onlinetime, 
                CS.level,
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                {extra_select_sql}
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY CS.level DESC, C.onlinetime DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_adena(limit=10, adn_billion_item=0, value_item=1000000):
        # Otimização: usar LEFT JOIN ao invés de subqueries correlacionadas
        # Isso é muito mais rápido pois permite uso de índices
        bonus_join = ""
        bonus_select = ""
        if adn_billion_item != 0:
            bonus_join = """
            LEFT JOIN (
                SELECT owner_id, SUM(count) * :value_item AS bonus_adenas
                FROM items
                WHERE item_id = :adn_billion_item
                GROUP BY owner_id
            ) I2 ON I2.owner_id = C.obj_Id
            """
            bonus_select = "IFNULL(I2.bonus_adenas, 0) +"
        
        sql = f"""
            SELECT 
                C.char_name, 
                C.online, 
                C.onlinetime, 
                CS.level, 
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                ({bonus_select} IFNULL(I1.adenas, 0)) AS adenas
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            LEFT JOIN (
                SELECT owner_id, SUM(count) AS adenas
                FROM items
                WHERE item_id = '57'
                GROUP BY owner_id
            ) I1 ON I1.owner_id = C.obj_Id
            {bonus_join}
            WHERE C.accesslevel = '0'
            ORDER BY adenas DESC, C.onlinetime DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {
            "limit": limit,
            "adn_billion_item": adn_billion_item,
            "value_item": value_item
        })

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_clans(limit=10):
        sql = f"""
            SELECT 
                C.clan_id, 
                S.name AS clan_name,
                C.clan_level, 
                C.reputation_score, 
                C.ally_id,
                NULL AS char_name, 
                (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS membros
            FROM clan_data C
            LEFT JOIN clan_subpledges S ON S.clan_id = C.clan_id AND S.type = 0
            ORDER BY C.clan_level DESC, C.reputation_score DESC, membros DESC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def olympiad_ranking():
        sql = """
            SELECT 
                C.char_name, 
                C.online, 
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                CS.class_id AS base, 
                O.olympiad_points
            FROM olympiad_nobles O
            LEFT JOIN characters C ON C.obj_Id = O.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
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
                D.name AS clan_name, 
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                CS.class_id AS base, 
                H.count
            FROM heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
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
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                CS.class_id AS base
            FROM heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE H.played > 0 AND H.count > 0
            ORDER BY base ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def grandboss_status():
        sql = """
            SELECT bossId AS boss_id, respawnDate AS respawn
            FROM epic_boss_spawn
            ORDER BY respawnDate DESC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def raidboss_status():
        sql = """
            SELECT 
                B.id AS boss_id,
                B.respawn_delay AS respawn,
                CASE 
                    WHEN B.respawn_delay IS NULL OR B.respawn_delay = 0 THEN 'Alive'
                    WHEN (
                        (B.respawn_delay > 9999999999 AND B.respawn_delay > UNIX_TIMESTAMP() * 1000) OR
                        (B.respawn_delay <= 9999999999 AND B.respawn_delay > UNIX_TIMESTAMP())
                    ) THEN 'Dead'
                    ELSE 'Alive'
                END AS status,
                CASE 
                    WHEN B.respawn_delay IS NULL OR B.respawn_delay = 0 THEN NULL
                    WHEN B.respawn_delay > 9999999999 THEN FROM_UNIXTIME(B.respawn_delay / 1000)
                    ELSE FROM_UNIXTIME(B.respawn_delay)
                END AS respawn_human
            FROM raidboss_status B
            ORDER BY respawn DESC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege():
        sql = f"""
            SELECT 
                W.id, 
                W.name, 
                W.siege_date AS sdate, 
                W.treasury AS stax,
                NULL AS char_name, 
                S.name AS clan_name,
                CLAN.clan_id,
                CLAN.ally_id,
                A.ally_name
            FROM castle W
            LEFT JOIN clan_data CLAN ON CLAN.hasCastle = W.id
            LEFT JOIN clan_subpledges S ON S.clan_id = CLAN.clan_id AND S.type = 0
            LEFT JOIN ally_data A ON A.ally_id = CLAN.ally_id
        """
        return LineageStats._run_query(sql)

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

    @staticmethod
    @cache_lineage_result(timeout=300)
    def search_characters(query, limit=20):
        """Busca personagens por nome (busca parcial)"""
        sql = """
            SELECT 
                C.obj_Id as char_id,
                C.char_name, 
                CS.level,
                CS.class_id AS base,
                C.online,
                C.lastAccess,
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                C.x,
                C.y,
                C.z
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0' 
            AND C.char_name LIKE :query
            ORDER BY CS.level DESC, C.char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"query": f"%{query}%", "limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_clan_details(clan_name):
        """Busca detalhes de um clã específico por nome"""
        sql = """
            SELECT 
                C.clan_id, 
                S.name AS clan_name,
                C.clan_level AS level, 
                C.reputation_score AS reputation, 
                C.ally_id,
                (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS member_count,
                (SELECT char_name FROM characters WHERE clanid = C.clan_id AND accesslevel = '0' LIMIT 1) AS leader_name
            FROM clan_data C
            LEFT JOIN clan_subpledges S ON S.clan_id = C.clan_id AND S.type = 0
            WHERE S.name = :clan_name
            LIMIT 1
        """
        result = LineageStats._run_query(sql, {"clan_name": clan_name})
        return result[0] if result and len(result) > 0 else None




class LineageServices:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_chars(login):
        sql = """
            SELECT
                C.*,
                (SELECT BS.class_id FROM character_subclasses AS BS 
                WHERE BS.char_obj_id = C.obj_Id AND BS.isBase = '1' 
                LIMIT 1) AS base_class,
                (SELECT BS.level FROM character_subclasses AS BS 
                WHERE BS.char_obj_id = C.obj_Id AND BS.isBase = '1' 
                LIMIT 1) AS base_level,

                -- Subclass 1
                (SELECT S1.class_id FROM character_subclasses AS S1 
                WHERE S1.char_obj_id = C.obj_Id AND S1.isBase = '0' 
                LIMIT 0,1) AS subclass1,
                (SELECT S1.level FROM character_subclasses AS S1 
                WHERE S1.char_obj_id = C.obj_Id AND S1.isBase = '0' 
                LIMIT 0,1) AS subclass1_level,

                -- Subclass 2
                (SELECT S2.class_id FROM character_subclasses AS S2 
                WHERE S2.char_obj_id = C.obj_Id AND S2.isBase = '0' 
                LIMIT 1,1) AS subclass2,
                (SELECT S2.level FROM character_subclasses AS S2 
                WHERE S2.char_obj_id = C.obj_Id AND S2.isBase = '0' 
                LIMIT 1,1) AS subclass2_level,

                -- Subclass 3
                (SELECT S3.class_id FROM character_subclasses AS S3 
                WHERE S3.char_obj_id = C.obj_Id AND S3.isBase = '0' 
                LIMIT 2,1) AS subclass3,
                (SELECT S3.level FROM character_subclasses AS S3 
                WHERE S3.char_obj_id = C.obj_Id AND S3.isBase = '0' 
                LIMIT 2,1) AS subclass3_level,

                CS.name AS clan_name,
                CLAN.ally_id AS ally_id
            FROM characters AS C
            LEFT JOIN clan_subpledges CS ON CS.clan_id = C.clanid AND CS.type = 0
            LEFT JOIN clan_data CLAN ON CLAN.clan_id = C.clanid
            WHERE C.account_name = :login
            LIMIT 7;
        """
        try:
            return LineageDB().select(sql, {"login": login})
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_char(acc, cid):
        sql = "SELECT * FROM characters WHERE obj_Id = :cid AND account_name = :acc LIMIT 1"
        try:
            return LineageDB().select(sql, {"acc": acc, "cid": cid})
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_name_exists(name):
        sql = "SELECT * FROM characters WHERE char_name = :name LIMIT 1"
        try:
            return LineageDB().select(sql, {"name": name})
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def change_nickname(acc, cid, name):
        try:
            sql = """
                UPDATE characters
                SET char_name = :name
                WHERE obj_Id = :cid AND account_name = :acc
                LIMIT 1
            """
            return LineageDB().update(sql, {"name": name, "cid": cid, "acc": acc})
        except Exception as e:
            print(f"Erro ao trocar nickname: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def change_sex(acc, cid, sex):
        try:
            sql = """
                UPDATE characters SET sex = :sex
                WHERE obj_Id = :cid AND account_name = :acc
                LIMIT 1
            """
            return LineageDB().update(sql, {"sex": sex, "cid": cid, "acc": acc})
        except Exception as e:
            print(f"Erro ao trocar sexo: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def unstuck(acc, cid, x, y, z):
        try:
            sql = """
                UPDATE characters SET x = :x, y = :y, z = :z
                WHERE obj_Id = :cid AND account_name = :acc
                LIMIT 1
            """
            return LineageDB().update(sql, {"x": x, "y": y, "z": z, "cid": cid, "acc": acc})
        except Exception as e:
            print(f"Erro ao desbugar personagem: {e}")
            return None




class LineageAccount:
    _checked_columns = False

    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_acess_level():
        return 'access_level'

    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_account_by_login(login):
        sql = """
            SELECT *
            FROM accounts
            WHERE login = :login
            LIMIT 1
        """
        try:
            result = LineageDB().select(sql, {"login": login})
            return result[0] if result else None
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_accounts_by_email(email):
        sql = """
            SELECT *
            FROM accounts
            WHERE email = :email
        """
        try:
            return LineageDB().select(sql, {"email": email})
        except:
            return []

    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_account_by_login_and_email(login, email):
        sql = """
            SELECT *
            FROM accounts
            WHERE login = :login AND email = :email
            LIMIT 1
        """
        try:
            result = LineageDB().select(sql, {"login": login, "email": email})
            return result[0] if result else None
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def link_account_to_user(login, user_uuid):
        try:
            sql = """
                UPDATE accounts
                SET linked_uuid = :uuid
                WHERE login = :login AND (linked_uuid IS NULL OR linked_uuid = '')
                LIMIT 1
            """
            params = {
                "uuid": str(user_uuid),
                "login": login
            }
            return LineageDB().update(sql, params)
        except Exception as e:
            print(f"Erro ao vincular conta Lineage a UUID: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def unlink_account_from_user(login, user_uuid):
        """Desvincula uma conta do Lineage de um UUID de usuário."""
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            user_uuid_str = str(user_uuid).strip()
            login_str = str(login).strip()
            
            check_sql = """
                SELECT login, linked_uuid, email
                FROM accounts
                WHERE login = :login
            """
            check_result = LineageDB().select(check_sql, {"login": login_str})
            
            if not check_result or len(check_result) == 0:
                logger.warning(f"Conta {login_str} não encontrada")
                return False
            
            account = check_result[0]
            current_uuid = account.get("linked_uuid") if isinstance(account, dict) else getattr(account, 'linked_uuid', None)
            
            if not current_uuid or str(current_uuid).strip() != user_uuid_str:
                return False
            
            sql = """
                UPDATE accounts
                SET linked_uuid = NULL
                WHERE login = :login
            """
            result = LineageDB().update(sql, {"login": login_str})
            
            return result is not None and result > 0
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao desvincular conta: {e}")
            return False

    @staticmethod
    @cache_lineage_result(timeout=300)
    def ensure_columns():
        if LineageAccount._checked_columns:
            return

        lineage_db = LineageDB()
        
        if not lineage_db.enabled:
            LineageAccount._checked_columns = True
            return
            
        columns = lineage_db.get_table_columns("accounts")
        # Se não foi possível obter as colunas (ex.: timeout), não tenta ADD COLUMN
        if not columns:
            LineageAccount._checked_columns = True
            return

        try:
            if "email" not in columns:
                sql = """
                    ALTER TABLE accounts
                    ADD COLUMN email VARCHAR(100) NOT NULL DEFAULT '';
                """
                if lineage_db.execute_raw(sql):
                    print("✅ Coluna 'email' adicionada com sucesso.")

            if "created_time" not in columns:
                sql = """
                    ALTER TABLE accounts
                    ADD COLUMN created_time INT(11) NULL DEFAULT NULL;
                """
                if lineage_db.execute_raw(sql):
                    print("✅ Coluna 'created_time' adicionada com sucesso.")

            if "linked_uuid" not in columns:
                sql = """
                    ALTER TABLE accounts
                    ADD COLUMN linked_uuid VARCHAR(36) NULL DEFAULT NULL;
                """
                if lineage_db.execute_raw(sql):
                    print("✅ Coluna 'linked_uuid' adicionada com sucesso.")

            LineageAccount._checked_columns = True

        except Exception as e:
            print(f"❌ Erro ao alterar tabela 'accounts': {e}")

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def check_login_exists(login):
        sql = "SELECT * FROM accounts WHERE login = :login LIMIT 1"
        return LineageDB().select(sql, {"login": login})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_email_exists(email):
        sql = "SELECT login, email FROM accounts WHERE email = :email"
        return LineageDB().select(sql, {"email": email})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def register(login, password, access_level, email):
        try:
            LineageAccount.ensure_columns()
            hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            sql = """
                INSERT INTO accounts (login, password, access_level, email, created_time)
                VALUES (:login, :password, :access_level, :email, :created_time)
            """
            params = {
                "login": login,
                "password": hashed,
                "access_level": access_level,
                "email": email,
                "created_time": int(time.time())
            }
            LineageDB().insert(sql, params)
            return True
        except Exception as e:
            print(f"Erro ao registrar conta: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_password(password, login):
        try:
            hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            sql = """
                UPDATE accounts SET password = :password
                WHERE login = :login LIMIT 1
            """
            params = {
                "password": hashed,
                "login": login
            }
            LineageDB().update(sql, params)
            return True
        except Exception as e:
            print(f"Erro ao atualizar senha: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_password_group(password, logins_list):
        if not logins_list:
            return None
        try:
            hashed = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            sql = "UPDATE accounts SET password = :password WHERE login IN :logins"
            params = {
                "password": hashed,
                "logins": logins_list
            }
            LineageDB().update(sql, params)
            return True
        except Exception as e:
            print(f"Erro ao atualizar senhas em grupo: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def update_access_level(access, login):
        try:
            sql = """
                UPDATE accounts SET access_level = :access
                WHERE login = :login LIMIT 1
            """
            params = {
                "access": access,
                "login": login
            }
            return LineageDB().update(sql, params)
        except Exception as e:
            print(f"Erro ao atualizar accessLevel: {e}")
            return None

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def validate_credentials(login, password):
        try:
            sql = "SELECT password FROM accounts WHERE login = :login LIMIT 1"
            result = LineageDB().select(sql, {"login": login})

            if not result:
                return False

            hashed_input = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()
            stored_hash = result[0]['password']
            return hashed_input == stored_hash

        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False




class TransferFromWalletToChar:
    items_delayed = True

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def find_char(account: str, char_name: str):
        query = """
            SELECT * FROM characters 
            WHERE account_name = :account AND char_name = :char_name 
            LIMIT 1
        """
        try:
            return LineageDB().select(query, {"account": account, "char_name": char_name})
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def search_coin(char_name: str, coin_id: int):
        query = """
            SELECT i.* FROM items i
            JOIN characters c ON i.owner_id = c.obj_Id
            WHERE c.char_name = :char_name AND i.item_id = :coin_id
        """
        return LineageDB().select(query, {"char_name": char_name, "coin_id": coin_id})

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def insert_coin(char_name: str, coin_id: int, amount: int, enchant: int = 0, force_stackable: bool = False):
        """
        Insere moedas/itens para um personagem.
        
        Parâmetros:
        - char_name: Nome do personagem
        - coin_id: ID do item/moeda
        - amount: Quantidade
        - enchant: Nível de encantamento (padrão: 0)
        - force_stackable: Se True, força o item como acumulável (stackable), 
                           ignorando a detecção automática. Útil para itens de donate.
        """
        db = LineageDB()
        
        # Verifica conexão antes de começar
        if not db.is_connected():
            print(f"⚠️ Banco Lineage desconectado ao tentar inserir moedas para {char_name}")
            return None

        # Buscar owner_id do personagem
        char_query = "SELECT obj_Id FROM characters WHERE char_name = :char_name"
        char_result = db.select(char_query, {"char_name": char_name})
        if not char_result:
            return None

        owner_id = char_result[0]["obj_Id"]

        # Verificar na tabela items (itens já processados) se o item é stackable
        # Verificar se as colunas enchant_level e loc existem antes de usar
        existing_items = []
        columns = db.get_table_columns("items")
        has_enchant_level = 'enchant_level' in columns
        has_loc = 'loc' in columns
        
        # Construir query dinamicamente baseado nas colunas disponíveis
        where_conditions = ["owner_id = :owner_id", "item_id = :coin_id"]
        query_params = {"owner_id": owner_id, "coin_id": coin_id}
        
        if has_enchant_level:
            where_conditions.append("enchant_level = :enchant")
            query_params["enchant"] = enchant
        
        if has_loc:
            where_conditions.append("loc = 'INVENTORY'")
        
        try:
            existing_items_query = f"""
                SELECT * FROM items
                WHERE {' AND '.join(where_conditions)}
            """
            existing_items = db.select(existing_items_query, query_params)
        except Exception:
            # Se falhar, buscar todos e filtrar em Python
            try:
                existing_items_query = """
                    SELECT * FROM items
                    WHERE owner_id = :owner_id 
                    AND item_id = :coin_id
                """
                all_items = db.select(existing_items_query, {
                    "owner_id": owner_id,
                    "coin_id": coin_id
                })
                # Filtrar por enchant e loc em Python
                for item in all_items:
                    item_enchant = item.get('enchant_level') or item.get('enchant') or item.get('enchantLevel') or 0
                    item_loc = item.get('loc') or item.get('location') or ''
                    
                    # Verificar enchant se necessário
                    if has_enchant_level and item_enchant != enchant:
                        continue
                    
                    # Verificar loc se necessário
                    if has_loc and item_loc != 'INVENTORY':
                        continue
                    
                    existing_items.append(item)
            except Exception:
                # Se ainda falhar, continuar sem verificação (fail-safe)
                existing_items = []

        # Detectar se o item é stackable (acumulável)
        # Se force_stackable=True, sempre trata como stackable (útil para itens de donate)
        if force_stackable:
            is_stackable = True
        else:
            # Lógica de detecção automática baseada nos itens existentes
            # Se existe apenas 1 item com count > 1, é stackable
            # Se existem múltiplos itens com count = 1, não é stackable
            is_stackable = False
            if existing_items:
                if len(existing_items) == 1 and existing_items[0]["count"] > 1:
                    is_stackable = True
                elif len(existing_items) == 1 and existing_items[0]["count"] == 1:
                    # Se tem apenas 1 item com count = 1, pode ser stackable ou não
                    is_stackable = True
                else:
                    # Múltiplos itens = não stackable
                    is_stackable = False

        # Validar coin_id se for muito grande (SMALLINT tem limite de 32767)
        # Se a coluna item_id for SMALLINT e o valor > 32767, vai dar erro
        # Nesse caso, é necessário alterar o schema do banco:
        # ALTER TABLE items_delayed MODIFY item_id INT UNSIGNED;
        if coin_id > 32767:
            # Tentar usar CAST para garantir conversão correta
            # Mas se a coluna for SMALLINT, isso ainda pode falhar
            pass

        # Detectar quais colunas existem na tabela items_delayed
        columns = db.get_table_columns("items_delayed")
        
        # Colunas obrigatórias
        cols_to_insert = ['payment_id', 'owner_id', 'item_id', 'count']
        values_to_insert = ['COALESCE(MAX(payment_id), 0) + 1', ':owner_id', ':coin_id', ':count_value']
        
        # Adicionar enchant se existir
        if 'enchant_level' in columns:
            cols_to_insert.append('enchant_level')
            values_to_insert.append(':enchant')
        
        # Adicionar colunas opcionais se existirem
        optional_cols = {
            'variationId1': '0',
            'variationId2': '0',
            'flags': '0',
            'payment_status': '0',
            'description': "'DONATE WEB'"
        }
        
        for col, value in optional_cols.items():
            if col in columns:
                cols_to_insert.append(col)
                values_to_insert.append(value)
        
        # Montar query dinamicamente
        cols_str = ', '.join(cols_to_insert)
        values_str = ', '.join(values_to_insert)
        
        # Se é stackable, inserir um único registro com a quantidade total
        if is_stackable:
            insert_query = f"""
                INSERT INTO items_delayed ({cols_str})
                SELECT {values_str}
                FROM items_delayed
            """
            try:
                result = db.insert(insert_query, {
                    "owner_id": owner_id,
                    "coin_id": coin_id,
                    "count_value": amount,
                    "enchant": enchant
                })
                return result is not None
            except Exception as e:
                print(f"❌ Erro ao inserir moedas (stackable): {e}")
                return None
        else:
            # Não stackable: inserir múltiplos registros usando BATCH INSERT
            # Limita a quantidade para evitar timeout e abusos
            MAX_NON_STACKABLE = 500  # Limite máximo de itens não-stackable por vez
            if amount > MAX_NON_STACKABLE:
                print(f"⚠️ Quantidade muito grande ({amount}) para item não-stackable, limitando a {MAX_NON_STACKABLE}")
                amount = MAX_NON_STACKABLE
            
            try:
                # Buscar o próximo payment_id uma única vez
                max_id_query = "SELECT COALESCE(MAX(payment_id), 0) as max_id FROM items_delayed"
                max_result = db.select(max_id_query)
                next_payment_id = (max_result[0]["max_id"] if max_result else 0) + 1
                
                # Construir valores para cada registro
                # Precisamos substituir os placeholders dinâmicos pelos valores reais
                union_parts = []
                for i in range(amount):
                    payment_id = next_payment_id + i
                    # Substituir placeholders pelos valores reais
                    values_row = values_str.replace(':owner_id', str(owner_id))
                    values_row = values_row.replace(':coin_id', str(coin_id))
                    values_row = values_row.replace(':count_value', '1')
                    values_row = values_row.replace(':enchant', str(enchant))
                    values_row = values_row.replace('COALESCE(MAX(payment_id), 0) + 1', str(payment_id))
                    union_parts.append(f"SELECT {values_row}")
                
                union_query = " UNION ALL ".join(union_parts)
                batch_insert_query = f"""
                    INSERT INTO items_delayed ({cols_str})
                    {union_query}
                """
                
                # Executar batch insert em uma única transação
                result = db.insert(batch_insert_query, {})
                if result is not None:
                    return True
                else:
                    print(f"❌ Erro ao executar batch insert de {amount} itens não-stackable")
                    return False
                    
            except Exception as e:
                print(f"❌ Erro ao inserir {amount} itens não-stackable em batch: {e}")
                return False




class TransferFromCharToWallet:

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def find_char(account, char_id):
        query = """
            SELECT online, char_name FROM characters 
            WHERE account_name = :account AND obj_Id = :char_id
        """
        params = {"account": account, "char_id": char_id}
        return LineageDB().select(query, params)

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def list_items(char_id):
        query = """
            SELECT object_id AS item_id, item_id AS item_type, count AS amount, loc AS location, enchant_level AS enchant
            FROM items
            WHERE owner_id = :char_id
            AND loc IN ('INVENTORY', 'WAREHOUSE')
            ORDER BY loc, item_id
        """
        params = {"char_id": char_id}
        results = LineageDB().select(query, params)
        return results

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def check_ingame_coin(coin_id, char_id):
        db = LineageDB()

        query_inve = """
            SELECT count AS amount, enchant_level AS enchant FROM items 
            WHERE owner_id = :char_id AND item_id = :coin_id AND loc = 'INVENTORY'
            LIMIT 1
        """
        result_inve = db.select(query_inve, {"char_id": char_id, "coin_id": coin_id})
        inINVE = result_inve[0]["amount"] if result_inve else 0
        enchant = result_inve[0]["enchant"] if result_inve else 0

        query_ware = """
            SELECT count AS amount FROM items 
            WHERE owner_id = :char_id AND item_id = :coin_id AND loc = 'WAREHOUSE'
            LIMIT 1
        """
        result_ware = db.select(query_ware, {"char_id": char_id, "coin_id": coin_id})
        inWARE = result_ware[0]["amount"] if result_ware else 0

        total = inINVE + inWARE
        return {"total": total, "inventory": inINVE, "warehouse": inWARE, "enchant": enchant}

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def remove_ingame_coin(coin_id, count, char_id):
        try:
            db = LineageDB()

            def delete_non_stackable(items, amount_to_remove):
                removed = 0
                for item in items:
                    if removed >= amount_to_remove:
                        break
                    db.update("DELETE FROM items WHERE object_id = :item_id", {"item_id": item["object_id"]})
                    removed += 1
                return removed

            query_inve = """
                SELECT * FROM items
                WHERE owner_id = :char_id AND item_id = :item_id AND loc = 'INVENTORY'
            """
            items_inve = db.select(query_inve, {"char_id": char_id, "item_id": coin_id})

            query_ware = """
                SELECT * FROM items
                WHERE owner_id = :char_id AND item_id = :item_id AND loc = 'WAREHOUSE'
            """
            items_ware = db.select(query_ware, {"char_id": char_id, "item_id": coin_id})

            total_amount = sum(item["count"] for item in items_inve + items_ware)
            if total_amount < count:
                return False

            is_stackable = len(items_inve + items_ware) == 1 and (items_inve + items_ware)[0]["count"] > 1

            if is_stackable:
                if items_inve:
                    item = items_inve[0]
                    if item["count"] <= count:
                        db.update("DELETE FROM items WHERE object_id = :item_id", {"item_id": item["object_id"]})
                        count -= item["count"]
                    else:
                        db.update(
                            "UPDATE items SET count = count - :count WHERE object_id = :item_id",
                            {"count": count, "item_id": item["object_id"]}
                        )
                        count = 0

                if count > 0 and items_ware:
                    item = items_ware[0]
                    if item["count"] <= count:
                        db.update("DELETE FROM items WHERE object_id = :item_id", {"item_id": item["object_id"]})
                    else:
                        db.update(
                            "UPDATE items SET count = count - :count WHERE object_id = :item_id",
                            {"count": count, "item_id": item["object_id"]}
                        )

            else:
                removed = delete_non_stackable(items_inve, count)
                if removed < count:
                    delete_non_stackable(items_ware, count - removed)

            return True

        except Exception as e:
            print(f"Erro ao remover coin do inventário/warehouse: {e}")
            return False

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def check_offline_variable(char_id):
        """
        Verifica se o personagem tem a variável 'offline' ativa (loja offline ou atividade ativa).
        Retorna True se encontrar a variável, False caso contrário.
        """
        try:
            db = LineageDB()
            # Tenta com obj_id primeiro (minúsculo), depois obj_Id (maiúsculo)
            query = """
                SELECT * FROM character_variables 
                WHERE obj_id = :char_id AND type = 'user-var' AND name = 'offline'
                LIMIT 1
            """
            result = db.select(query, {"char_id": char_id})
            if result:
                return True
            
            # Se não encontrou, tenta com obj_Id (maiúsculo) para compatibilidade
            query_alt = """
                SELECT * FROM character_variables 
                WHERE obj_Id = :char_id AND type = 'user-var' AND name = 'offline'
                LIMIT 1
            """
            result_alt = db.select(query_alt, {"char_id": char_id})
            return bool(result_alt)
        except Exception as e:
            print(f"⚠️ Erro ao verificar variável offline: {e}")
            return False


class LineageMarketplace:
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def get_user_characters(account_name):
        """Busca todos os characters de uma conta do banco L2."""
        sql = f"""
            SELECT 
                c.obj_Id as char_id,
                c.char_name,
                (SELECT BS.level FROM character_subclasses BS WHERE BS.char_obj_id = c.obj_Id AND BS.isBase = '1' LIMIT 1) AS level,
                (SELECT BS.class_id FROM character_subclasses BS WHERE BS.char_obj_id = c.obj_Id AND BS.isBase = '1' LIMIT 1) AS classid,
                c.pvpkills as pvp_kills,
                c.pkkills as pk_count,
                c.clanid,
                COALESCE(cs.name, '') as clan_name,
                c.accesslevel,
                c.online,
                c.lastAccess,
                c.account_name
            FROM characters c
            LEFT JOIN clan_data cd ON c.clanid = cd.clan_id
            LEFT JOIN clan_subpledges cs ON cs.clan_id = cd.clan_id AND cs.type = 0
            WHERE c.account_name = :account_name
            ORDER BY level DESC, c.char_name ASC
        """
        return LineageDB().select(sql, {"account_name": account_name})
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def verify_character_ownership(char_id, account_name):
        """Verifica se um character pertence a uma conta específica."""
        sql = """
            SELECT COUNT(*) as total
            FROM characters 
            WHERE obj_Id = :char_id AND account_name = :account_name
        """
        result = LineageDB().select(sql, {"char_id": char_id, "account_name": account_name})
        return result[0]['total'] > 0 if result and len(result) > 0 else False
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def get_character_details(char_id):
        """Busca detalhes completos de um character do banco L2."""
        sql = f"""
            SELECT 
                c.obj_Id as char_id,
                c.char_name,
                (SELECT BS.level FROM character_subclasses BS WHERE BS.char_obj_id = c.obj_Id AND BS.isBase = '1' LIMIT 1) AS level,
                (SELECT BS.class_id FROM character_subclasses BS WHERE BS.char_obj_id = c.obj_Id AND BS.isBase = '1' LIMIT 1) AS classid,
                c.pvpkills as pvp_kills,
                c.pkkills as pk_count,
                c.clanid,
                COALESCE(cs.name, '') as clan_name,
                c.accesslevel,
                c.online,
                c.lastAccess,
                c.account_name
            FROM characters c
            LEFT JOIN clan_data cd ON c.clanid = cd.clan_id
            LEFT JOIN clan_subpledges cs ON cs.clan_id = cd.clan_id AND cs.type = 0
            WHERE c.obj_Id = :char_id
        """
        result = LineageDB().select(sql, {"char_id": char_id})
        return result[0] if result and len(result) > 0 else None
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def get_character_items_count(char_id):
        """Conta quantos itens um character possui no banco L2."""
        sql = """
            SELECT COUNT(*) as total_items
            FROM items 
            WHERE owner_id = :char_id
            AND (loc = 'INVENTORY' OR loc = 'PAPERDOLL')
        """
        result = LineageDB().select(sql, {"char_id": char_id})
        return result[0]['total_items'] if result and len(result) > 0 else 0
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def get_character_items(char_id):
        """Busca todos os itens de um character do banco L2."""
        sql = """
            SELECT 
                i.object_id,
                i.item_id,
                i.count,
                i.enchant_level,
                i.loc,
                i.loc_data
            FROM items i
            WHERE i.owner_id = :char_id
            AND (i.loc = 'INVENTORY' OR i.loc = 'PAPERDOLL')
            ORDER BY i.loc, i.loc_data
        """
        result = LineageDB().select(sql, {"char_id": char_id})
        
        if result is None:
            return {'inventory': [], 'equipment': []}
        
        inventory_items = []
        equipment_items = []
        
        for item_data in result:
            if item_data['loc'] == 'INVENTORY':
                inventory_items.append(item_data)
            elif item_data['loc'] == 'PAPERDOLL':
                equipment_items.append(item_data)
        
        return {
            'inventory': inventory_items,
            'equipment': equipment_items
        }
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def count_characters_in_account(account_name):
        """Conta quantos personagens existem em uma conta."""
        sql = """
            SELECT COUNT(*) as total
            FROM characters 
            WHERE account_name = :account_name
        """
        result = LineageDB().select(sql, {"account_name": account_name})
        return result[0]['total'] if result and len(result) > 0 else 0
    
    @staticmethod
    def create_or_update_marketplace_account(account_name, password_hash):
        """Cria ou atualiza a conta mestre do marketplace no banco L2."""
        db = LineageDB()
        
        check_sql = "SELECT login FROM accounts WHERE login = :account_name"
        existing = db.select(check_sql, {"account_name": account_name})
        
        try:
            if existing and len(existing) > 0:
                update_sql = """
                    UPDATE accounts 
                    SET password = :password_hash,
                        access_level = 0,
                        lastactive = UNIX_TIMESTAMP()
                    WHERE login = :account_name
                """
                result = db.update(update_sql, {
                    "password_hash": password_hash,
                    "account_name": account_name
                })
                return result is not None and result > 0
            else:
                insert_sql = """
                    INSERT INTO accounts (login, password, access_level, lastactive)
                    VALUES (:account_name, :password_hash, 0, UNIX_TIMESTAMP())
                """
                result = db.insert(insert_sql, {
                    "account_name": account_name,
                    "password_hash": password_hash
                })
                return result is not None
        except Exception as e:
            print(f"❌ Erro ao criar/atualizar conta: {e}")
            return False
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def transfer_character_to_account(char_id, new_account):
        """Transfere um character para nova conta no banco L2."""
        sql = "UPDATE characters SET account_name = :new_account WHERE obj_Id = :char_id"
        result = LineageDB().update(sql, {"new_account": new_account, "char_id": char_id})
        return result is not None and result > 0




class LineageInflation:
    """Classe para análise de inflação de itens no servidor."""

    @staticmethod
    def _run_query(sql, params=None, use_cache=False):
        return LineageDB().select(sql, params=params, use_cache=use_cache)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_all_items_by_location():
        """Busca todos os itens de todos os personagens, agrupados por localização."""
        sql = """
            SELECT 
                i.item_id AS item_id,
                i.count AS quantity,
                i.loc AS location,
                i.owner_id,
                c.char_name,
                c.account_name,
                CONCAT('Item ', i.item_id) AS item_name,
                NULL AS item_category,
                NULL AS crystal_type,
                i.enchant_level AS enchant
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.loc IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            ORDER BY i.loc, i.item_id, c.char_name
        """
        return LineageInflation._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_items_summary_by_category():
        """Resumo de itens agrupados por categoria e localização."""
        sql = """
            SELECT 
                i.item_id AS item_id,
                CONCAT('Item ', i.item_id) AS item_name,
                NULL AS item_category,
                NULL AS crystal_type,
                i.loc AS location,
                COUNT(*) AS total_instances,
                SUM(i.count) AS total_quantity,
                COUNT(DISTINCT i.owner_id) AS unique_owners,
                MIN(i.enchant_level) AS min_enchant,
                MAX(i.enchant_level) AS max_enchant,
                AVG(i.enchant_level) AS avg_enchant
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.loc IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            GROUP BY i.item_id, i.loc
            ORDER BY total_quantity DESC, item_id ASC
        """
        return LineageInflation._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_items_by_character(char_id=None):
        """Busca todos os itens de um personagem específico ou de todos."""
        if char_id:
            sql = """
                SELECT 
                    i.item_id AS item_id,
                    i.count AS quantity,
                    i.loc AS location,
                    i.owner_id,
                    c.char_name,
                    c.account_name,
                    CONCAT('Item ', i.item_id) AS item_name,
                    i.enchant_level AS enchant
                FROM items i
                INNER JOIN characters c ON c.obj_Id = i.owner_id
                WHERE i.owner_id = :char_id
                AND i.loc IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
                ORDER BY i.loc, i.item_id
            """
            return LineageInflation._run_query(sql, {"char_id": char_id})
        else:
            return LineageInflation.get_all_items_by_location()

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_top_items_by_quantity(limit=100):
        """Retorna os itens mais comuns no servidor."""
        sql = """
            SELECT 
                i.item_id AS item_id,
                CONCAT('Item ', i.item_id) AS item_name,
                SUM(i.count) AS total_quantity,
                COUNT(DISTINCT i.owner_id) AS unique_owners,
                COUNT(*) AS total_instances
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.loc IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            GROUP BY i.item_id
            ORDER BY total_quantity DESC
            LIMIT :limit
        """
        return LineageInflation._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_items_by_location_summary():
        """Resumo de itens por localização."""
        sql = """
            SELECT 
                i.loc AS location,
                COUNT(DISTINCT i.item_id) AS unique_item_types,
                COUNT(*) AS total_instances,
                SUM(i.count) AS total_quantity,
                COUNT(DISTINCT i.owner_id) AS unique_owners
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.loc IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            GROUP BY i.loc
            ORDER BY i.loc
        """
        return LineageInflation._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_site_items_count():
        """Conta itens armazenados no site."""
        return []

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_inflation_comparison(date_from=None, date_to=None):
        """Compara a quantidade de itens entre duas datas."""
        return {
            "date_from": date_from,
            "date_to": date_to,
            "items": []
        }


class LineageClans:

    @staticmethod
    def get_user_lead_clans(account_logins):
        if not account_logins:
            return []
        db = LineageDB()
        if not getattr(db, 'enabled', False):
            return []
        placeholders = ", ".join([f":acc{i}" for i in range(len(account_logins))])
        params = {f"acc{i}": acc for i, acc in enumerate(account_logins)}
        sub_filter = "S.sub_pledge_id = 0" if SUBPLEDGE_FILTER == 'sub_pledge_id' else "S.type = 0"
        if CLAN_NAME_SOURCE == 'clan_data':
            sql = f"""
                SELECT C.clan_id, C.clan_name, C.clan_level, P.char_name AS leader_name, P.{CHAR_ID} AS leader_id
                FROM clan_data C
                INNER JOIN characters P ON P.{CHAR_ID} = C.leader_id
                WHERE P.account_name IN ({placeholders})
            """
        else:
            sql = f"""
                SELECT C.clan_id, S.name AS clan_name, C.clan_level, P.char_name AS leader_name, P.{CHAR_ID} AS leader_id
                FROM clan_data C
                INNER JOIN clan_subpledges S ON S.clan_id = C.clan_id AND {sub_filter}
                INNER JOIN characters P ON P.{CHAR_ID} = S.leader_id
                WHERE P.account_name IN ({placeholders})
            """
        try:
            result = db.select(sql, params)
            return result if result else []
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"LineageClans.get_user_lead_clans: {e}")
            return []

    @staticmethod
    def get_user_characters(account_logins):
        if not account_logins:
            return []
        all_characters = []
        for login in account_logins:
            try:
                personagens = LineageServices.find_chars(login)
                if personagens:
                    for char in personagens:
                        all_characters.append({
                            'char_id': char.get(CHAR_ID) or char.get('obj_Id') or char.get('obj_id') or char.get('charId'),
                            'char_name': char.get('char_name'),
                            'account_name': char.get('account_name', login),
                            'level': char.get('base_level') or char.get('level', 1),
                            'clan_id': char.get('clanid', 0) or char.get('clan_id', 0)
                        })
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"LineageClans.get_user_characters: {e}")
        return all_characters

    @staticmethod
    def get_clan_basic_info(clan_id):
        db = LineageDB()
        if not getattr(db, 'enabled', False):
            return None
        sub_filter = "S.sub_pledge_id = 0" if SUBPLEDGE_FILTER == 'sub_pledge_id' else "S.type = 0"
        if CLAN_NAME_SOURCE == 'clan_data':
            sql = "SELECT clan_id, clan_name, clan_level FROM clan_data WHERE clan_id = :clan_id"
        else:
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
            logging.getLogger(__name__).error(f"LineageClans.get_clan_basic_info: {e}")
            return None

    @staticmethod
    def get_clan_full_details(clan_id):
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
        """Retorna os membros de um clã (Mobius)."""
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
                    C.accesslevel
                FROM characters C
                WHERE C.clanid = :clan_id
                ORDER BY C.online DESC, level DESC, C.char_name ASC
            """
            result = db.select(sql, {"clan_id": clan_id})
            return result if result else []
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"LineageClans.get_clan_members: {e}")
            return []

