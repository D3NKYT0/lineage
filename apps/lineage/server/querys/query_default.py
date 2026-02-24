from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result

import time
import base64
import hashlib

from apps.lineage.server.utils.password_hash import PasswordHash


# ============================================================================
# CONFIGURAÇÃO DO SCHEMA - Default (compatível com DreamV3/L2J)
# ============================================================================
# Use estas constantes nas views ao invés de valores hardcoded:
#   ❌ ERRADO: account['accesslevel']
#   ✅ CERTO:  account[ACCESS_LEVEL]

CHAR_ID = 'obj_Id'  # Queries usam C.obj_Id
ACCESS_LEVEL = 'accesslevel'
BASE_CLASS_COL = 'class_id'  # Vem de character_subclasses
HAS_SUBCLASS = True
SUBCLASS_CHAR_ID = 'char_obj_id'
CLAN_NAME_SOURCE = 'clan_subpledges'  # Usa D.name de clan_subpledges
SUBPLEDGE_FILTER = 'type'  # sub_pledge_id ou type
HAS_ALLY_DATA = False

# ============================================================================


def detect_and_hash(password, stored_hash, login=None):
    hash_len = len(stored_hash)

    if hash_len == 28:
        hasher = PasswordHash("sha1")
    elif hash_len == 88:
        hasher = PasswordHash("whirlpool")
    else:
        return None  # hash desconhecido

    return hasher.encrypt(password)


class LineageStats:

    @staticmethod
    def _run_query(sql, params=None, use_cache=True):
        return LineageDB().select(sql, params=params, use_cache=use_cache)
    
    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_crests(ids, type='clan'):
        # Verifique se os IDs foram fornecidos
        if not ids:
            return []

        # Defina a tabela e a coluna do emblema com base no tipo (clan ou ally)
        if type == 'ally':
            table = 'ally_data'
            id_column = 'ally_id'
            crest_column = 'crest'
        else:
            table = 'clan_data'
            id_column = 'clan_id'
            crest_column = 'crest'

        # Construção da consulta SQL para obter as crests dos clãs ou alianças
        sql = f"""
            SELECT {id_column}, {crest_column}
            FROM {table}
            WHERE {id_column} IN :ids
        """
        
        # Chama a função _run_query para executar a consulta
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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY level DESC, exp DESC, onlinetime DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_level_with_extra_column(extra_select_sql, limit=20):
        """
        Top Level com coluna extra. O extra_select_sql deve ser validado antes.
        Ex: (SELECT COUNT(*) FROM items WHERE owner_id = C.obj_Id) AS total_items
        """
        # Injetar após ally_id, antes do FROM
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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY level DESC, exp DESC, onlinetime DESC, char_name ASC
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
                SELECT owner_id, SUM(amount) * :value_item AS bonus_adenas
                FROM items
                WHERE item_type = :adn_billion_item
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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            LEFT JOIN (
                SELECT owner_id, SUM(amount) AS adenas
                FROM items
                WHERE item_type = '57'
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
        sql = """
            SELECT C.clan_id, D.name AS clan_name, C.clan_level, C.reputation_score, A.ally_name, A.ally_id,
                   P.char_name, 
                   (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS membros
            FROM clan_data C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clan_id AND D.type = '0'
            LEFT JOIN ally_data A ON A.ally_id = C.ally_id
            LEFT JOIN characters P ON P.obj_Id = D.leader_id
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
                O.points_current AS olympiad_points
            FROM oly_nobles O
            LEFT JOIN characters C ON C.obj_Id = O.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
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
                CLAN.ally_id AS ally_id,
                CS.class_id AS base, 
                H.count
            FROM oly_heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CLAN ON CLAN.clan_id = C.clanid
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
                CLAN.ally_id AS ally_id,
                CS.class_id AS base
            FROM oly_heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.isBase = '1'
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
            LEFT JOIN clan_data CLAN ON CLAN.clan_id = C.clanid
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
            SELECT B.id AS boss_id, B.respawn_delay AS respawn, N.name, N.level
            FROM raidboss_status B
            INNER JOIN site_bosses N ON N.id = B.id
            ORDER BY respawn DESC, level DESC, name ASC
            SELECT bossId AS boss_id, respawnDate AS respawn
            FROM epic_boss_spawn
            ORDER BY respawnDate DESC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege():
        sql = """
            SELECT 
                W.id, 
                W.name, 
                W.siege_date AS sdate, 
                W.treasury AS stax,
                P.char_name, 
                CS.name AS clan_name,
                C.clan_id,
                C.ally_id,
                A.ally_name
            FROM castle W
            LEFT JOIN clan_data C ON C.hasCastle = W.id
            LEFT JOIN clan_subpledges CS ON CS.clan_id = C.clan_id AND CS.type = '0'
            LEFT JOIN ally_data A ON A.ally_id = C.ally_id
            LEFT JOIN characters P ON P.obj_Id = CS.leader_id
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege_participants(castle_id):
        sql = """
            SELECT 
                S.type, 
                C.name AS clan_name,
                C.clan_id
            FROM siege_clans S
            LEFT JOIN clan_subpledges C ON C.clan_id = S.clan_id AND C.type = '0'
            WHERE S.residence_id = :castle_id
        """
        return LineageStats._run_query(sql, {"castle_id": castle_id})

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
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.type = '0'
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
            LEFT JOIN clan_subpledges S ON S.clan_id = C.clan_id AND S.type = '0'
            WHERE S.name = :clan_name
            LIMIT 1
        """
        result = LineageStats._run_query(sql, {"clan_name": clan_name})
        return result[0] if result and len(result) > 0 else None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def boss_jewel_locations(boss_jewel_ids):
        # Gera bind dinâmico para IN
        bind_ids = [f":id{i}" for i in range(len(boss_jewel_ids))]
        placeholders = ", ".join(bind_ids)
        sql = f"""
            SELECT 
                I.owner_id, 
                I.item_type AS item_id, 
                SUM(I.amount) AS count,
                C.char_name,
                P.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id
            FROM items I
            INNER JOIN characters C ON C.obj_Id = I.owner_id
            LEFT JOIN clan_subpledges P ON P.clan_id = C.clanid AND P.type = '0'
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE I.item_type IN ({placeholders})
            GROUP BY I.owner_id, C.char_name, P.name, I.item_type, C.clanid, CD.ally_id
            ORDER BY count DESC, C.char_name ASC
        """
        params = {f"id{i}": item_id for i, item_id in enumerate(boss_jewel_ids)}
        return LineageStats._run_query(sql, params)


class LineageServices:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_chars(login):
        sql = """
            SELECT
                C.*, 
                -- Base class e level
                (SELECT S0.class_id FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS base_class,
                (SELECT S0.level FROM character_subclasses AS S0 WHERE S0.char_obj_id = C.obj_Id AND S0.isBase = '1' LIMIT 1) AS base_level,

                -- Subclass 1
                (SELECT S1.class_id FROM character_subclasses AS S1 WHERE S1.char_obj_id = C.obj_Id AND S1.isBase = '0' LIMIT 0,1) AS subclass1,
                (SELECT S1.level FROM character_subclasses AS S1 WHERE S1.char_obj_id = C.obj_Id AND S1.isBase = '0' LIMIT 0,1) AS subclass1_level,

                -- Subclass 2
                (SELECT S2.class_id FROM character_subclasses AS S2 WHERE S2.char_obj_id = C.obj_Id AND S2.isBase = '0' LIMIT 1,1) AS subclass2,
                (SELECT S2.level FROM character_subclasses AS S2 WHERE S2.char_obj_id = C.obj_Id AND S2.isBase = '0' LIMIT 1,1) AS subclass2_level,

                -- Subclass 3
                (SELECT S3.class_id FROM character_subclasses AS S3 WHERE S3.char_obj_id = C.obj_Id AND S3.isBase = '0' LIMIT 2,1) AS subclass3,
                (SELECT S3.level FROM character_subclasses AS S3 WHERE S3.char_obj_id = C.obj_Id AND S3.isBase = '0' LIMIT 2,1) AS subclass3_level,

                -- Clan e Ally
                CS.name AS clan_name,
                A.ally_name
            FROM characters AS C
            LEFT JOIN clan_data AS CLAN ON CLAN.clan_id = C.clanid
            LEFT JOIN clan_subpledges AS CS ON CS.clan_id = CLAN.clan_id
            LEFT JOIN ally_data AS A ON A.ally_id = CLAN.ally_id
            WHERE C.account_name = :login
            LIMIT 7
        """
        try:
            return LineageDB().select(sql, {"login": login})
        except:
            return None

    @staticmethod
    @cache_lineage_result(timeout=300)
    def check_char(acc, cid):
        sql = "SELECT * FROM characters WHERE obj_id = :cid AND account_name = :acc LIMIT 1"
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
                WHERE obj_id = :cid AND account_name = :acc
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
                WHERE obj_id = :cid AND account_name = :acc
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
        return 'accessLevel'
    
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
        """
        Desvincula uma conta do Lineage de um UUID de usuário.
        Remove apenas o linked_uuid da conta (o email não é alterado pois pode ser NOT NULL).
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Normaliza o UUID para comparação
            user_uuid_str = str(user_uuid).strip()
            login_str = str(login).strip()
            
            logger.info(f"[unlink_account_from_user] Tentando desvincular conta {login_str} do UUID {user_uuid_str}")
            
            # Primeiro verifica se a conta existe e está vinculada
            check_sql = """
                SELECT login, linked_uuid, email
                FROM accounts
                WHERE login = :login
            """
            check_params = {"login": login_str}
            check_result = LineageDB().select(check_sql, check_params)
            
            if not check_result or len(check_result) == 0:
                logger.warning(f"[unlink_account_from_user] Conta {login_str} não encontrada")
                return False
            
            account = check_result[0]
            current_uuid = account.get("linked_uuid") if isinstance(account, dict) else getattr(account, 'linked_uuid', None)
            
            if current_uuid:
                current_uuid_str = str(current_uuid).strip()
                logger.info(f"[unlink_account_from_user] Conta {login_str} - linked_uuid atual: '{current_uuid_str}', esperado: '{user_uuid_str}'")
                
                if current_uuid_str != user_uuid_str:
                    logger.warning(f"[unlink_account_from_user] UUID não corresponde: '{current_uuid_str}' != '{user_uuid_str}'")
                    return False
            else:
                logger.warning(f"[unlink_account_from_user] Conta {login_str} não está vinculada (linked_uuid é NULL)")
                return False
            
            # Agora faz o UPDATE - como já verificamos que está vinculada, podemos fazer direto
            # Não setamos email = NULL porque o banco pode não permitir
            sql = """
                UPDATE accounts
                SET linked_uuid = NULL
                WHERE login = :login
            """
            params = {
                "login": login_str
            }
            result = LineageDB().update(sql, params)
            
            logger.info(f"[unlink_account_from_user] Resultado do UPDATE: {result}")
            
            if result is not None and result > 0:
                logger.info(f"[unlink_account_from_user] Conta {login_str} desvinculada com sucesso")
                return True
            else:
                logger.warning(f"[unlink_account_from_user] UPDATE não afetou nenhuma linha para conta {login_str}")
                return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[unlink_account_from_user] Erro ao desvincular conta Lineage do UUID: {e}", exc_info=True)
            print(f"Erro ao desvincular conta Lineage do UUID: {e}")
            return False

    @staticmethod
    @cache_lineage_result(timeout=300)
    def ensure_columns():
        if LineageAccount._checked_columns:
            return

        lineage_db = LineageDB()
        
        # Verifica se o banco está habilitado antes de tentar qualquer operação
        if not lineage_db.enabled:
            LineageAccount._checked_columns = True
            return
            
        columns = lineage_db.get_table_columns("accounts")
        # Se não foi possível obter as colunas (ex.: timeout), não tenta ADD COLUMN
        # para evitar erro "Duplicate column name" quando as colunas já existem
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
                INSERT INTO accounts (login, password, accessLevel, email, created_time)
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
                UPDATE accounts SET accessLevel = :access
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

            stored_hash: str = result[0]['password']
            hashed_input = detect_and_hash(password, stored_hash)

            return hashed_input.lower() == stored_hash.lower()

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

        # Se é stackable, inserir um único registro com a quantidade total
        if is_stackable:
            insert_query = """
                INSERT INTO items_delayed (
                    payment_id, owner_id, item_id, count,
                    enchant_level, variationId1, variationId2,
                    flags, payment_status, description
                )
                SELECT
                    COALESCE(MAX(payment_id), 0) + 1,
                    :owner_id, :coin_id, :amount,
                    :enchant, 0, 0,
                    0, 0, 'DONATE WEB'
                FROM items_delayed
            """
            try:
                result = db.insert(insert_query, {
                    "owner_id": owner_id,
                    "coin_id": coin_id,
                    "amount": amount,
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
                
                # Construir query de batch INSERT usando UNION ALL
                # Isso insere todos os registros em uma única transação (muito mais eficiente)
                union_parts = []
                for i in range(amount):
                    payment_id = next_payment_id + i
                    union_parts.append(
                        f"SELECT {payment_id}, {owner_id}, {coin_id}, 1, {enchant}, 0, 0, 0, 0, 'DONATE WEB'"
                    )
                
                union_query = " UNION ALL ".join(union_parts)
                batch_insert_query = f"""
                    INSERT INTO items_delayed (
                        payment_id, owner_id, item_id, count,
                        enchant_level, variationId1, variationId2,
                        flags, payment_status, description
                    )
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
            SELECT item_id, item_type, amount, location, enchant
            FROM items
            WHERE owner_id = :char_id
            AND location IN ('INVENTORY', 'WAREHOUSE')
            ORDER BY location, item_type
        """
        params = {"char_id": char_id}
        results = LineageDB().select(query, params)

        return results

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def check_ingame_coin(coin_id, char_id):
        db = LineageDB()

        # Buscar no INVENTORY
        query_inve = """
            SELECT amount, enchant FROM items 
            WHERE owner_id = :char_id AND item_type = :coin_id AND location = 'INVENTORY'
            LIMIT 1
        """
        result_inve = db.select(query_inve, {"char_id": char_id, "coin_id": coin_id})
        inINVE = result_inve[0]["amount"] if result_inve else 0
        enchant = result_inve[0]["enchant"] if result_inve else 0

        # Buscar no WAREHOUSE
        query_ware = """
            SELECT amount FROM items 
            WHERE owner_id = :char_id AND item_type = :coin_id AND location = 'WAREHOUSE'
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

            # Função auxiliar para deletar itens não stackables
            def delete_non_stackable(items, amount_to_remove):
                removed = 0
                for item in items:
                    if removed >= amount_to_remove:
                        break
                    db.update("DELETE FROM items WHERE item_id = :item_id", {"item_id": item["item_id"]})
                    removed += 1
                return removed

            # INVENTORY
            query_inve = """
                SELECT * FROM items
                WHERE owner_id = :char_id AND item_type = :item_type AND location = 'INVENTORY'
            """
            items_inve = db.select(query_inve, {"char_id": char_id, "item_type": coin_id})

            # WAREHOUSE
            query_ware = """
                SELECT * FROM items
                WHERE owner_id = :char_id AND item_type = :item_type AND location = 'WAREHOUSE'
            """
            items_ware = db.select(query_ware, {"char_id": char_id, "item_type": coin_id})

            total_amount = sum(item["amount"] for item in items_inve + items_ware)
            if total_amount < count:
                return False  # Não tem quantidade suficiente

            # Identifica se é stackable ou não
            is_stackable = len(items_inve + items_ware) == 1 and (items_inve + items_ware)[0]["amount"] > 1

            if is_stackable:
                # Remove do INVENTORY primeiro
                if items_inve:
                    item = items_inve[0]
                    if item["amount"] <= count:
                        db.update("DELETE FROM items WHERE item_id = :item_id", {"item_id": item["item_id"]})
                        count -= item["amount"]
                    else:
                        db.update(
                            "UPDATE items SET amount = amount - :count WHERE item_id = :item_id",
                            {"count": count, "item_id": item["item_id"]}
                        )
                        count = 0

                # Se ainda faltar, remove do WAREHOUSE
                if count > 0 and items_ware:
                    item = items_ware[0]
                    if item["amount"] <= count:
                        db.update("DELETE FROM items WHERE item_id = :item_id", {"item_id": item["item_id"]})
                    else:
                        db.update(
                            "UPDATE items SET amount = amount - :count WHERE item_id = :item_id",
                            {"count": count, "item_id": item["item_id"]}
                        )

            else:
                # Não stackável – remover 1 a 1, primeiro INVENTORY depois WAREHOUSE
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
        """
        Busca todos os characters de uma conta do banco L2.
        Retorna apenas dados das tabelas originais do Lineage 2.
        Schema: Dream v3 (usa obj_Id, level em character_subclasses)
        """
        sql = """
            SELECT 
                c.obj_Id as char_id,
                c.char_name,
                (SELECT S0.level FROM character_subclasses AS S0 WHERE S0.char_obj_id = c.obj_Id AND S0.isBase = '1' LIMIT 1) AS level,
                (SELECT S0.class_id FROM character_subclasses AS S0 WHERE S0.char_obj_id = c.obj_Id AND S0.isBase = '1' LIMIT 1) AS classid,
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
            LEFT JOIN clan_subpledges cs ON cs.clan_id = cd.clan_id AND cs.type = '0'
            WHERE c.account_name = :account_name
            ORDER BY level DESC, c.char_name ASC
        """
        return LineageDB().select(sql, {"account_name": account_name})
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def verify_character_ownership(char_id, account_name):
        """
        Verifica se um character pertence a uma conta específica.
        Schema: Dream v3 (usa obj_Id)
        """
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
        """
        Busca detalhes completos de um character do banco L2.
        Schema: Dream v3 (usa obj_Id, level em character_subclasses)
        """
        sql = """
            SELECT 
                c.obj_Id as char_id,
                c.char_name,
                (SELECT S0.level FROM character_subclasses AS S0 WHERE S0.char_obj_id = c.obj_Id AND S0.isBase = '1' LIMIT 1) AS level,
                (SELECT S0.class_id FROM character_subclasses AS S0 WHERE S0.char_obj_id = c.obj_Id AND S0.isBase = '1' LIMIT 1) AS classid,
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
            LEFT JOIN clan_subpledges cs ON cs.clan_id = cd.clan_id AND cs.type = '0'
            WHERE c.obj_Id = :char_id
        """
        result = LineageDB().select(sql, {"char_id": char_id})
        return result[0] if result and len(result) > 0 else None
    
    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def get_character_items_count(char_id):
        """
        Conta quantos itens um character possui no banco L2.
        Schema: Dream v3 (usa obj_Id)
        """
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
        """
        Busca todos os itens de um character do banco L2.
        Retorna dict com 'inventory' e 'equipment'.
        Schema: Dream v3 (usa obj_Id)
        """
        sql = """
            SELECT 
                i.object_id,
                i.item_id,
                i.count,
                i.enchant_level,
                i.loc,
                i.loc_data,
                COALESCE(it.name, 'Item Desconhecido') as item_name,
                it.icon,
                it.item_type,
                it.crystal_type
            FROM items i
            LEFT JOIN item_templates it ON i.item_id = it.item_id
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
        """
        Conta quantos personagens existem em uma conta.
        Usado para validar o limite de 7 personagens do Lineage 2.
        Schema: Dream v3 (usa obj_Id)
        """
        sql = """
            SELECT COUNT(*) as total
            FROM characters 
            WHERE account_name = :account_name
        """
        result = LineageDB().select(sql, {"account_name": account_name})
        return result[0]['total'] if result and len(result) > 0 else 0
    
    @staticmethod
    def create_or_update_marketplace_account(account_name, password_hash):
        """
        Cria ou atualiza a conta mestre do marketplace no banco L2.
        Schema: Dream v3
        
        Returns:
            bool: True se sucesso, False se falhou
        """
        db = LineageDB()
        
        # Verifica se a conta já existe
        check_sql = "SELECT login FROM accounts WHERE login = :account_name"
        existing = db.select(check_sql, {"account_name": account_name})
        
        try:
            if existing and len(existing) > 0:
                # Atualiza conta existente
                update_sql = """
                    UPDATE accounts 
                    SET password = :password_hash,
                        accessLevel = 0,
                        lastactive = UNIX_TIMESTAMP()
                    WHERE login = :account_name
                """
                result = db.update(update_sql, {
                    "password_hash": password_hash,
                    "account_name": account_name
                })
                return result is not None and result > 0
            else:
                # Cria nova conta
                insert_sql = """
                    INSERT INTO accounts (login, password, accessLevel, lastactive)
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
        """
        Transfere um character para nova conta no banco L2.
        Altera o campo account_name na tabela characters.
        Schema: Dream v3 (usa obj_Id)
        
        IMPORTANTE: Esta operação modifica dados críticos do jogo.
        Deve ser usado apenas após validação completa da transação.
        """
        sql = "UPDATE characters SET account_name = :new_account WHERE obj_Id = :char_id"
        result = LineageDB().update(sql, {"new_account": new_account, "char_id": char_id})
        return result is not None and result > 0


class LineageInflation:
    """
    Classe para análise de inflação de itens no servidor.
    Verifica todos os inventários dos jogadores, categoriza itens e rastreia onde estão armazenados.
    """

    @staticmethod
    def _run_query(sql, params=None, use_cache=False):
        return LineageDB().select(sql, params=params, use_cache=use_cache)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_all_items_by_location():
        """
        Busca todos os itens de todos os personagens, agrupados por localização.
        Schema: Dream v3 (usa item_type, amount, location)
        Retorna: Lista de itens com informações de localização
        """
        sql = """
            SELECT 
                i.item_type AS item_id,
                i.amount AS quantity,
                i.location,
                i.owner_id,
                c.char_name,
                c.account_name,
                CONCAT('Item ', i.item_type) AS item_name,
                NULL AS item_category,
                NULL AS crystal_type,
                i.enchant_level AS enchant
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.location IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            ORDER BY i.location, i.item_type, c.char_name
        """
        return LineageInflation._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_items_summary_by_category():
        """
        Resumo de itens agrupados por categoria e localização.
        Schema: Dream v3
        Retorna: Estatísticas agregadas por item e localização
        """
        sql = """
            SELECT 
                i.item_type AS item_id,
                CONCAT('Item ', i.item_type) AS item_name,
                NULL AS item_category,
                NULL AS crystal_type,
                i.location,
                COUNT(*) AS total_instances,
                SUM(i.amount) AS total_quantity,
                COUNT(DISTINCT i.owner_id) AS unique_owners,
                MIN(i.enchant_level) AS min_enchant,
                MAX(i.enchant_level) AS max_enchant,
                AVG(i.enchant_level) AS avg_enchant
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.location IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            GROUP BY i.item_type, i.location
            ORDER BY total_quantity DESC, item_id ASC
        """
        return LineageInflation._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_items_by_character(char_id=None):
        """
        Busca todos os itens de um personagem específico ou de todos.
        Schema: Dream v3
        """
        if char_id:
            sql = """
                SELECT 
                    i.item_type AS item_id,
                    i.amount AS quantity,
                    i.location,
                    i.owner_id,
                    c.char_name,
                    c.account_name,
                    CONCAT('Item ', i.item_type) AS item_name,
                    NULL AS item_category,
                    i.enchant_level AS enchant
                FROM items i
                INNER JOIN characters c ON c.obj_Id = i.owner_id
                WHERE i.owner_id = :char_id
                AND i.location IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
                ORDER BY i.location, i.item_type
            """
            return LineageInflation._run_query(sql, {"char_id": char_id})
        else:
            return LineageInflation.get_all_items_by_location()

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_top_items_by_quantity(limit=100):
        """
        Retorna os itens mais comuns no servidor.
        Schema: Dream v3
        """
        sql = """
            SELECT 
                i.item_type AS item_id,
                CONCAT('Item ', i.item_type) AS item_name,
                NULL AS item_category,
                SUM(i.amount) AS total_quantity,
                COUNT(DISTINCT i.owner_id) AS unique_owners,
                COUNT(*) AS total_instances
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.location IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            GROUP BY i.item_type
            ORDER BY total_quantity DESC
            LIMIT :limit
        """
        return LineageInflation._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_items_by_location_summary():
        """
        Resumo de itens por localização (Inventário, Baú, Equipado, Baú do Clã).
        Schema: Dream v3
        """
        sql = """
            SELECT 
                i.location,
                COUNT(DISTINCT i.item_type) AS unique_item_types,
                COUNT(*) AS total_instances,
                SUM(i.amount) AS total_quantity,
                COUNT(DISTINCT i.owner_id) AS unique_owners
            FROM items i
            INNER JOIN characters c ON c.obj_Id = i.owner_id
            WHERE c.accesslevel = '0'
            AND i.location IN ('INVENTORY', 'WAREHOUSE', 'PAPERDOLL', 'CLANWH')
            GROUP BY i.location
            ORDER BY i.location
        """
        return LineageInflation._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_site_items_count():
        """
        Conta itens armazenados no site (inventário do site).
        Precisa ser integrado com o modelo Inventory do Django.
        Retorna: Contagem de itens no site
        """
        # Esta query será complementada pela integração com Django
        # Por enquanto retorna estrutura vazia
        return []

    @staticmethod
    @cache_lineage_result(timeout=60, use_cache=False)
    def get_inflation_comparison(date_from=None, date_to=None):
        """
        Compara a quantidade de itens entre duas datas (requer snapshots salvos).
        Esta função será usada em conjunto com os modelos Django.
        """
        # Esta função será implementada com os snapshots do Django
        return {
            "date_from": date_from,
            "date_to": date_to,
            "items": []
        }


class LineageClans:

    @staticmethod
    def get_user_lead_clans(account_logins):
        """Retorna clãs onde algum personagem das contas é líder."""
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
        """Retorna personagens das contas usando LineageServices.find_chars."""
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
        """Retorna info básica do clã (clan_id, clan_name, clan_level)."""
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
        """Retorna os membros de um clã (Base/Default L2J)."""
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
            try:
                # Fallback mais básico caso caracteristicas avancadas não existam
                sql_fallback = "SELECT char_name, online FROM characters WHERE clanid = :clan_id OR clan_id = :clan_id ORDER BY online DESC, char_name ASC"
                result = db.select(sql_fallback, {"clan_id": clan_id})
                return result if result else []
            except:
                import logging
                logging.getLogger(__name__).error(f"LineageClans.get_clan_members (fallback): {e}")
                return []