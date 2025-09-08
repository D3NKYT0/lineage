from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result

import time
import base64
import hashlib
from datetime import datetime


class LineageStats:

    @staticmethod
    def _run_query(sql, params=None, use_cache=True):
        return LineageDB().select(sql, params=params, use_cache=use_cache)
    
    @staticmethod
    @cache_lineage_result(timeout=300)
    def get_crests(ids, type='clan'):
        if not ids:
            return []

        table = 'clan_data'
        id_column = 'clan_id'
        crest_column = 'crest_id'

        sql = f"""
            SELECT {id_column}, {crest_column}
            FROM {table}
            WHERE {id_column} IN :ids
        """
        return LineageStats._run_query(sql, {"ids": tuple(ids)})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def players_online():
        sql = "SELECT COUNT(*) AS quant FROM characters WHERE online > 0 AND accessLevel = '0'"
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
                C.level,
                C.classid AS base,
                D.clan_name,
                C.clanid AS clan_id,
                D.ally_id
            FROM characters C
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
            WHERE C.accessLevel = '0'
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
                C.level,
                C.classid AS base,
                D.clan_name,
                C.clanid AS clan_id,
                D.ally_id
            FROM characters C
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
            WHERE C.accessLevel = '0'
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
                C.level,
                C.classid AS base,
                D.clan_name,
                C.clanid AS clan_id,
                D.ally_id
            FROM characters C
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
            WHERE C.accessLevel = '0'
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
                C.level,
                D.clan_name,
                C.clanid AS clan_id,
                D.ally_id
            FROM characters C
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
            WHERE C.accessLevel = '0'
            ORDER BY level DESC, exp DESC, onlinetime DESC, char_name ASC
            LIMIT :limit
        """
        return LineageStats._run_query(sql, {"limit": limit})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def top_adena(limit=10, adn_billion_item=0, value_item=1000000):
        item_bonus_sql = ""
        if adn_billion_item != 0:
            item_bonus_sql = f"""
                IFNULL((SELECT SUM(I2.count) * :value_item
                        FROM items I2
                        WHERE I2.owner_id = C.charId AND I2.item_id = :adn_billion_item
                        GROUP BY I2.owner_id), 0) +
            """
        sql = f"""
            SELECT 
                C.char_name, 
                C.online, 
                C.onlinetime, 
                C.level, 
                D.clan_name,
                C.clanid AS clan_id,
                D.ally_id,
                (
                    {item_bonus_sql}
                    IFNULL((SELECT SUM(I1.count)
                            FROM items I1
                            WHERE I1.owner_id = C.charId AND I1.item_id = '57'
                            GROUP BY I1.owner_id), 0)
                ) AS adenas
            FROM characters C
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
            WHERE C.accessLevel = '0'
            ORDER BY adenas DESC, onlinetime DESC, char_name ASC
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
            SELECT 
                C.clan_id, 
                C.clan_name, 
                C.clan_level, 
                C.reputation_score, 
                C.ally_name,
                C.ally_id,
                P.char_name, 
                (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS membros
            FROM clan_data C
            LEFT JOIN characters P ON P.charId = C.leader_id
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
                D.clan_name,
                C.clanid AS clan_id,
                D.ally_id,
                O.class_id AS base, 
                O.olympiad_points
            FROM olympiad_nobles O
            LEFT JOIN characters C ON C.charId = O.charId
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
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
                D.clan_name, 
                D.ally_name, 
                H.class_id AS base, 
                H.count
            FROM heroes H
            LEFT JOIN characters C ON C.charId = H.charId
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
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
                D.clan_name,
                D.ally_name,
                H.class_id AS base
            FROM heroes H
            LEFT JOIN characters C ON C.charId = H.charId
            LEFT JOIN clan_data D ON D.clan_id = C.clanid
            WHERE H.played > 0 AND H.count > 0
            ORDER BY base ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def grandboss_status():
        sql = """
            SELECT 
                B.boss_id, 
                B.respawn_time AS respawn, 
                CASE B.boss_id
                    WHEN 29001 THEN 'Queen Ant'
                    WHEN 29006 THEN 'Core'
                    WHEN 29014 THEN 'Orfen'
                    WHEN 29019 THEN 'Antharas'
                    WHEN 29020 THEN 'Baium'
                    WHEN 29022 THEN 'Zaken'
                    WHEN 29028 THEN 'Valakas'
                    WHEN 29045 THEN 'Frintezza'
                    WHEN 29046 THEN 'Frintezza'
                    WHEN 29047 THEN 'Frintezza'
                    WHEN 29048 THEN 'Frintezza'
                    WHEN 29049 THEN 'Frintezza'
                    WHEN 29050 THEN 'Frintezza'
                    WHEN 29051 THEN 'Frintezza'
                    WHEN 29052 THEN 'Frintezza'
                    WHEN 29054 THEN 'Frintezza'
                    WHEN 29056 THEN 'Frintezza'
                    WHEN 29057 THEN 'Frintezza'
                    WHEN 29058 THEN 'Frintezza'
                    WHEN 29059 THEN 'Frintezza'
                    WHEN 29060 THEN 'Frintezza'
                    WHEN 29061 THEN 'Frintezza'
                    WHEN 29062 THEN 'Frintezza'
                    WHEN 29063 THEN 'Frintezza'
                    WHEN 29064 THEN 'Frintezza'
                    WHEN 29065 THEN 'Frintezza'
                    WHEN 29066 THEN 'Frintezza'
                    WHEN 29067 THEN 'Frintezza'
                    WHEN 29068 THEN 'Frintezza'
                    WHEN 29069 THEN 'Frintezza'
                    WHEN 29070 THEN 'Frintezza'
                    WHEN 29071 THEN 'Frintezza'
                    WHEN 29072 THEN 'Frintezza'
                    WHEN 29073 THEN 'Frintezza'
                    WHEN 29074 THEN 'Frintezza'
                    WHEN 29075 THEN 'Frintezza'
                    WHEN 29076 THEN 'Frintezza'
                    WHEN 29077 THEN 'Frintezza'
                    WHEN 29078 THEN 'Frintezza'
                    WHEN 29079 THEN 'Frintezza'
                    WHEN 29080 THEN 'Frintezza'
                    WHEN 29081 THEN 'Frintezza'
                    WHEN 29082 THEN 'Frintezza'
                    WHEN 29083 THEN 'Frintezza'
                    WHEN 29084 THEN 'Frintezza'
                    WHEN 29085 THEN 'Frintezza'
                    WHEN 29086 THEN 'Frintezza'
                    WHEN 29087 THEN 'Frintezza'
                    WHEN 29088 THEN 'Frintezza'
                    WHEN 29089 THEN 'Frintezza'
                    WHEN 29090 THEN 'Frintezza'
                    WHEN 29091 THEN 'Frintezza'
                    WHEN 29092 THEN 'Frintezza'
                    WHEN 29093 THEN 'Frintezza'
                    WHEN 29094 THEN 'Frintezza'
                    WHEN 29095 THEN 'Frintezza'
                    WHEN 29096 THEN 'Frintezza'
                    WHEN 29097 THEN 'Frintezza'
                    WHEN 29098 THEN 'Frintezza'
                    WHEN 29099 THEN 'Frintezza'
                    WHEN 29100 THEN 'Frintezza'
                    WHEN 29118 THEN 'Beleth'
                    WHEN 29163 THEN 'Frintezza'
                    WHEN 29164 THEN 'Frintezza'
                    WHEN 29165 THEN 'Frintezza'
                    WHEN 29166 THEN 'Frintezza'
                    WHEN 29167 THEN 'Frintezza'
                    WHEN 29168 THEN 'Frintezza'
                    WHEN 29169 THEN 'Frintezza'
                    WHEN 29170 THEN 'Frintezza'
                    WHEN 29171 THEN 'Frintezza'
                    WHEN 29172 THEN 'Frintezza'
                    WHEN 29173 THEN 'Frintezza'
                    WHEN 29174 THEN 'Frintezza'
                    WHEN 29175 THEN 'Frintezza'
                    WHEN 29176 THEN 'Frintezza'
                    WHEN 29177 THEN 'Frintezza'
                    WHEN 29178 THEN 'Frintezza'
                    WHEN 29179 THEN 'Frintezza'
                    WHEN 29180 THEN 'Frintezza'
                    WHEN 29181 THEN 'Frintezza'
                    WHEN 29182 THEN 'Frintezza'
                    WHEN 29183 THEN 'Frintezza'
                    WHEN 29184 THEN 'Frintezza'
                    WHEN 29185 THEN 'Frintezza'
                    WHEN 29186 THEN 'Frintezza'
                    WHEN 29187 THEN 'Frintezza'
                    WHEN 29188 THEN 'Frintezza'
                    WHEN 29189 THEN 'Frintezza'
                    WHEN 29190 THEN 'Frintezza'
                    WHEN 29191 THEN 'Frintezza'
                    WHEN 29192 THEN 'Frintezza'
                    WHEN 29193 THEN 'Frintezza'
                    WHEN 29194 THEN 'Frintezza'
                    WHEN 29195 THEN 'Frintezza'
                    WHEN 29196 THEN 'Frintezza'
                    WHEN 29197 THEN 'Frintezza'
                    WHEN 29198 THEN 'Frintezza'
                    WHEN 29199 THEN 'Frintezza'
                    WHEN 29200 THEN 'Frintezza'
                    ELSE 'Unknown Boss'
                END AS name
            FROM grandboss_data B
            ORDER BY respawn DESC, name ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege():
        sql = """
            SELECT 
                W.id, 
                W.name, 
                W.siegeDate AS sdate, 
                W.taxPercent AS stax,
                P.char_name, 
                C.clan_name,
                C.clan_id,
                C.ally_id,
                C.ally_name
            FROM castle W
            LEFT JOIN clan_data C ON C.hasCastle = W.id
            LEFT JOIN characters P ON P.charId = C.leader_id
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def siege_participants(castle_id):
        sql = """
            SELECT 
                S.type, 
                C.clan_name,
                C.clan_id
            FROM siege_clans S
            LEFT JOIN clan_data C ON C.clan_id = S.clan_id
            WHERE S.castle_id = :castle_id
        """
        return LineageStats._run_query(sql, {"castle_id": castle_id})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def boss_jewel_locations(boss_jewel_ids):
        sql = """
            SELECT 
                I.owner_id, 
                I.item_id, 
                SUM(I.count) AS count,
                C.char_name,
                P.clan_name,
                C.clanid AS clan_id,
                P.ally_id
            FROM items I
            INNER JOIN characters C ON C.charId = I.owner_id
            LEFT JOIN clan_data P ON P.clan_id = C.clanid
            WHERE I.item_id IN :boss_jewel_ids
            GROUP BY I.owner_id, C.char_name, P.clan_name, I.item_id, C.clanid, P.ally_id
            ORDER BY count DESC, C.char_name ASC
        """
        return LineageStats._run_query(sql, {"boss_jewel_ids": tuple(boss_jewel_ids)})


class LineageServices:

    @staticmethod
    @cache_lineage_result(timeout=300)
    def find_chars(login):
        sql = """
            SELECT
                C.*, 
                C.charId AS obj_Id,
                C.classid AS base_class,
                C.level AS base_level,
                (SELECT S1.class_id FROM character_subclasses AS S1 
                WHERE S1.charId = C.charId AND S1.class_index > 0 
                LIMIT 0,1) AS subclass1,
                (SELECT S1.level FROM character_subclasses AS S1 
                WHERE S1.charId = C.charId AND S1.class_index > 0 
                LIMIT 0,1) AS subclass1_level,
                (SELECT S2.class_id FROM character_subclasses AS S2 
                WHERE S2.charId = C.charId AND S2.class_index > 0 
                LIMIT 1,1) AS subclass2,
                (SELECT S2.level FROM character_subclasses AS S2 
                WHERE S2.charId = C.charId AND S2.class_index > 0 
                LIMIT 1,1) AS subclass2_level,
                (SELECT S3.class_id FROM character_subclasses AS S3 
                WHERE S3.charId = C.charId AND S3.class_index > 0 
                LIMIT 2,1) AS subclass3,
                (SELECT S3.level FROM character_subclasses AS S3 
                WHERE S3.charId = C.charId AND S3.class_index > 0 
                LIMIT 2,1) AS subclass3_level,
                D.clan_name,
                D.ally_name
            FROM characters AS C
            LEFT JOIN clan_data AS D ON D.clan_id = C.clanid
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
        sql = "SELECT * FROM characters WHERE charId = :cid AND account_name = :acc LIMIT 1"
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
                WHERE charId = :cid AND account_name = :acc
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
                WHERE charId = :cid AND account_name = :acc
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
                WHERE charId = :cid AND account_name = :acc
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
            current_time = datetime.fromtimestamp(int(time.time()))
            sql = """
                INSERT INTO accounts (login, password, accessLevel, email, created_time)
                VALUES (:login, :password, :access_level, :email, :created_time)
            """
            params = {
                "login": login,
                "password": hashed,
                "access_level": access_level,
                "email": email,
                "created_time": current_time
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

            hashed_input = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()

            stored_hash = result[0]['password']
            return hashed_input == stored_hash

        except Exception as e:
            print(f"Erro ao verificar senha: {e}")
            return False


class TransferFromWalletToChar:
    items_delayed = False

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
            JOIN characters c ON i.owner_id = c.charId
            WHERE c.char_name = :char_name AND i.item_id = :coin_id
        """
        return LineageDB().select(query, {"char_name": char_name, "coin_id": coin_id})

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def insert_coin(char_name: str, coin_id: int, amount: int, enchant: int = 0):
        db = LineageDB()

        # Get character ID
        char_query = "SELECT charId FROM characters WHERE char_name = :char_name"
        char_result = db.select(char_query, {"char_name": char_name})
        if not char_result:
            return None

        owner_id = char_result[0]["charId"]

        # Check if item already exists in inventory
        check_query = """
            SELECT object_id FROM items 
            WHERE owner_id = :owner_id 
            AND item_id = :coin_id 
            AND loc = 'INVENTORY' 
            LIMIT 1
        """
        existing_item = db.select(check_query, {
            "owner_id": owner_id,
            "coin_id": coin_id
        })

        if existing_item:
            # Item exists, update count
            object_id = existing_item[0]["object_id"]
            update_query = """
                UPDATE items 
                SET count = count + :amount 
                WHERE object_id = :object_id 
                AND owner_id = :owner_id 
                LIMIT 1
            """
            result = db.update(update_query, {
                "amount": amount,
                "object_id": object_id,
                "owner_id": owner_id
            })
            if not result:
                print(f"Erro ao atualizar item existente: {object_id}")
            else:
                print(f"Item existente atualizado com sucesso: {object_id}")
            return result

        # Item doesn't exist, create new one
        # Get last object_id
        last_object_query = "SELECT object_id FROM items ORDER BY object_id DESC LIMIT 1"
        last_object_result = db.select(last_object_query)
        if not last_object_result:
            new_object_id = 700000000
        else:
            last_object_id = int(last_object_result[0]["object_id"])
            new_object_id = last_object_id + 1

        # Get last loc_data for this owner
        last_loc_query = """
            SELECT loc_data FROM items 
            WHERE owner_id = :owner_id 
            ORDER BY loc_data DESC LIMIT 1
        """
        last_loc_result = db.select(last_loc_query, {"owner_id": owner_id})
        if not last_loc_result:
            new_loc_data = 0
        else:
            last_loc_data = int(last_loc_result[0]["loc_data"])
            new_loc_data = last_loc_data + 1

        # Get current timestamp
        creation_time = int(time.time())

        # Insert new item with all required fields
        insert_query = """
            INSERT INTO items (
                owner_id, object_id, item_id, count,
                enchant_level, loc, loc_data, process,
                creator_id, first_owner_id, creation_time
            ) VALUES (
                :owner_id, :object_id, :coin_id, :amount,
                :enchant, 'INVENTORY', :loc_data, 'admin_create',
                268501254, 268501254, :creation_time
            )
        """
        result = db.insert(insert_query, {
            "owner_id": owner_id,
            "object_id": new_object_id,
            "coin_id": coin_id,
            "amount": amount,
            "enchant": enchant,
            "loc_data": new_loc_data,
            "creation_time": creation_time
        })

        if not result:
            print(f"Erro ao criar novo item: {new_object_id}")
        else:
            print(f"Novo item criado com sucesso: {new_object_id}")

        return result is not None


class TransferFromCharToWallet:

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def find_char(account, char_id):
        query = """
            SELECT online, char_name FROM characters 
            WHERE account_name = :account AND charId = :char_id
        """
        return LineageDB().select(query, {"account": account, "char_id": char_id})

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
        return LineageDB().select(query, {"char_id": char_id})

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
