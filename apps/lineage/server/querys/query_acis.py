from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.cache import cache_lineage_result

import time
import base64
import hashlib


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

        # Como ally_data não existe, usaremos clan_data para ambos os tipos
        table = 'clan'
        
        # Defina a coluna do ID e do emblema com base no tipo (clan ou ally)
        if type == 'ally':
            id_column = 'id'
            crest_column = 'imagenes'  # Usando ally_crest_id da tabela clan_data
        else:
            id_column = 'id'
            crest_column = 'imagenes'  # Usando crest_id para clãs

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
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
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
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
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
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
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
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
            ORDER BY CS.level DESC, CS.exp DESC, C.onlinetime DESC, C.char_name ASC
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
                        WHERE I2.owner_id = C.obj_Id AND I2.item_id = :adn_billion_item
                        GROUP BY I2.owner_id), 0) +
            """
        sql = f"""
            SELECT 
                C.char_name, 
                C.online, 
                C.onlinetime, 
                CS.level, 
                D.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id AS ally_id,
                (
                    {item_bonus_sql}
                    IFNULL((SELECT SUM(I1.count)
                            FROM items I1
                            WHERE I1.owner_id = C.obj_Id AND I1.item_id = '57'
                            GROUP BY I1.owner_id), 0)
                ) AS adenas
            FROM characters C
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE C.accesslevel = '0'
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
                D.name AS clan_name, 
                C.clan_level, 
                C.reputation_score, 
                C.ally_name,  -- Obtendo ally_name diretamente de clan_data
                C.ally_id,
                P.char_name, 
                (SELECT COUNT(*) FROM characters WHERE clanid = C.clan_id) AS membros
            FROM clan_data C
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clan_id AND D.sub_pledge_id = 0
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
                O.olympiad_points
            FROM olympiad_nobles O
            LEFT JOIN characters C ON C.obj_Id = O.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
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
            FROM heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
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
            FROM heroes H
            LEFT JOIN characters C ON C.obj_Id = H.char_id
            LEFT JOIN character_subclasses CS ON CS.char_obj_id = C.obj_Id AND CS.class_index = 0
            LEFT JOIN clan_subpledges D ON D.clan_id = C.clanid AND D.sub_pledge_id = 0
            LEFT JOIN clan_data CLAN ON CLAN.clan_id = C.clanid
            WHERE H.played > 0 AND H.count > 0
            ORDER BY base ASC
        """
        return LineageStats._run_query(sql)

    @staticmethod
    @cache_lineage_result(timeout=300)
    def grandboss_status():
        sql = """
            SELECT boss_id, respawn_time AS respawn
            FROM grandboss_data
            ORDER BY respawn_time DESC
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
                W.treasury AS stax,
                P.char_name, 
                CS.name AS clan_name,
                C.clan_id,
                C.ally_id,
                C.ally_name  -- Obtendo ally_name diretamente de clan_data
            FROM castle W
            LEFT JOIN clan_data C ON C.hasCastle = W.id
            LEFT JOIN clan_subpledges CS ON CS.clan_id = C.clan_id AND CS.sub_pledge_id = 0
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
            LEFT JOIN clan_subpledges C ON C.clan_id = S.clan_id AND C.sub_pledge_id = 0
            WHERE S.castle_id = :castle_id
        """
        return LineageStats._run_query(sql, {"castle_id": castle_id})

    @staticmethod
    @cache_lineage_result(timeout=300)
    def boss_jewel_locations(boss_jewel_ids):
        # Gera bind dinâmico para IN
        bind_ids = [f":id{i}" for i in range(len(boss_jewel_ids))]
        placeholders = ", ".join(bind_ids)
        sql = f"""
            SELECT 
                I.owner_id, 
                I.item_id, 
                SUM(I.count) AS count,
                C.char_name,
                P.name AS clan_name,
                C.clanid AS clan_id,
                CD.ally_id
            FROM items I
            INNER JOIN characters C ON C.obj_Id = I.owner_id
            LEFT JOIN clan_subpledges P ON P.clan_id = C.clanid AND P.sub_pledge_id = 0
            LEFT JOIN clan_data CD ON CD.clan_id = C.clanid
            WHERE I.item_id IN ({placeholders})
            GROUP BY I.owner_id, C.char_name, P.name, I.item_id, C.clanid, CD.ally_id
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
                -- Base class e level diretamente da tabela characters
                C.classid AS base_class,
                C.level AS base_level,

                -- Subclass 1
                (SELECT S1.class_id FROM character_subclasses AS S1 
                WHERE S1.char_obj_id = C.obj_Id AND S1.class_index > 0 
                LIMIT 0,1) AS subclass1,
                (SELECT S1.level FROM character_subclasses AS S1 
                WHERE S1.char_obj_id = C.obj_Id AND S1.class_index > 0 
                LIMIT 0,1) AS subclass1_level,

                -- Subclass 2
                (SELECT S2.class_id FROM character_subclasses AS S2 
                WHERE S2.char_obj_id = C.obj_Id AND S2.class_index > 0 
                LIMIT 1,1) AS subclass2,
                (SELECT S2.level FROM character_subclasses AS S2 
                WHERE S2.char_obj_id = C.obj_Id AND S2.class_index > 0 
                LIMIT 1,1) AS subclass2_level,

                -- Subclass 3
                (SELECT S3.class_id FROM character_subclasses AS S3 
                WHERE S3.char_obj_id = C.obj_Id AND S3.class_index > 0 
                LIMIT 2,1) AS subclass3,
                (SELECT S3.level FROM character_subclasses AS S3 
                WHERE S3.char_obj_id = C.obj_Id AND S3.class_index > 0 
                LIMIT 2,1) AS subclass3_level,

                -- Clan e Ally
                CS.name AS clan_name,
                CLAN.ally_name
            FROM characters AS C
            LEFT JOIN clan_data AS CLAN ON CLAN.clan_id = C.clanid
            LEFT JOIN clan_subpledges AS CS ON CS.clan_id = CLAN.clan_id AND CS.sub_pledge_id = 0
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
            # Busca o hash salvo no banco
            sql = "SELECT password FROM accounts WHERE login = :login LIMIT 1"
            result = LineageDB().select(sql, {"login": login})

            if not result:
                return False

            # Calcula o hash da senha informada
            hashed_input = base64.b64encode(hashlib.sha1(password.encode()).digest()).decode()

            # Compara com o valor armazenado
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
            JOIN characters c ON i.owner_id = c.obj_Id
            WHERE c.char_name = :char_name AND i.item_id = :coin_id
        """
        return LineageDB().select(query, {"char_name": char_name, "coin_id": coin_id})

    @staticmethod
    @cache_lineage_result(timeout=300, use_cache=False)
    def insert_coin(char_name: str, coin_id: int, amount: int, enchant: int = 0):
        db = LineageDB()

        # Buscar owner_id
        char_query = "SELECT obj_Id FROM characters WHERE char_name = :char_name"
        char_result = db.select(char_query, {"char_name": char_name})
        if not char_result:
            return None

        owner_id = char_result[0]["obj_Id"]
        object_id = owner_id

        if object_id != 0:
            # Atualiza item existente
            update_query = """
                UPDATE items SET count = count + :amount
                WHERE object_id = :object_id AND owner_id = :owner_id
            """
            db.update(update_query, {
                "amount": amount,
                "object_id": object_id,
                "owner_id": owner_id
            })
            return True

        # Gerar novo object_id (começando com 7)
        last_object_query = """
            SELECT object_id FROM items 
            WHERE object_id LIKE '7%' 
            ORDER BY object_id DESC LIMIT 1
        """
        last_object_result = db.select(last_object_query)
        if not last_object_result:
            new_object_id = 700000000
        else:
            last_object_id = int(last_object_result[0]["object_id"])
            new_object_id = last_object_id + 1

        # Pegar o último loc_data do player
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

        # Inserir novo item
        insert_query = """
            INSERT INTO items (
                owner_id, object_id, item_id, count,
                enchant_level, loc, loc_data
            ) VALUES (
                :owner_id, :object_id, :coin_id, :amount,
                :enchant, 'INVENTORY', :loc_data
            )
        """
        result = db.insert(insert_query, {
            "owner_id": owner_id,
            "object_id": new_object_id,
            "coin_id": coin_id,
            "amount": amount,
            "enchant": enchant,
            "loc_data": new_loc_data
        })

        return result is not None


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

        # Buscar no INVENTORY
        query_inve = """
            SELECT count AS amount, enchant_level AS enchant FROM items 
            WHERE owner_id = :char_id AND item_id = :coin_id AND loc = 'INVENTORY'
            LIMIT 1
        """
        result_inve = db.select(query_inve, {"char_id": char_id, "coin_id": coin_id})
        inINVE = result_inve[0]["amount"] if result_inve else 0
        enchant = result_inve[0]["enchant"] if result_inve else 0

        # Buscar no WAREHOUSE
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

            # Função auxiliar para deletar itens não stackables
            def delete_non_stackable(items, amount_to_remove):
                removed = 0
                for item in items:
                    if removed >= amount_to_remove:
                        break
                    db.update("DELETE FROM items WHERE object_id = :item_id", {"item_id": item["object_id"]})
                    removed += 1
                return removed

            # INVENTORY
            query_inve = """
                SELECT * FROM items
                WHERE owner_id = :char_id AND item_id = :item_id AND loc = 'INVENTORY'
            """
            items_inve = db.select(query_inve, {"char_id": char_id, "item_id": coin_id})

            # WAREHOUSE
            query_ware = """
                SELECT * FROM items
                WHERE owner_id = :char_id AND item_id = :item_id AND loc = 'WAREHOUSE'
            """
            items_ware = db.select(query_ware, {"char_id": char_id, "item_id": coin_id})

            total_amount = sum(item["count"] for item in items_inve + items_ware)
            if total_amount < count:
                return False  # Não tem quantidade suficiente

            # Identifica se é stackable ou não
            is_stackable = len(items_inve + items_ware) == 1 and (items_inve + items_ware)[0]["count"] > 1

            if is_stackable:
                # Remove do INVENTORY primeiro
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

                # Se ainda faltar, remove do WAREHOUSE
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
                # Não stackável – remover 1 a 1, primeiro INVENTORY depois WAREHOUSE
                removed = delete_non_stackable(items_inve, count)
                if removed < count:
                    delete_non_stackable(items_ware, count - removed)

            return True

        except Exception as e:
            print(f"Erro ao remover coin do inventário/warehouse: {e}")
            return False
