import os
import time
import threading
from typing import Any, Dict, Tuple, List, Optional
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine, Result

load_dotenv()

class LineageDB:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LineageDB, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.engine: Optional[Engine] = None
        self.cache: Dict[Tuple[str, Tuple[Any, ...]], Tuple[List[Dict], float]] = {}
        self.cache_ttl = 60  # segundos
        self.enabled = os.getenv("LINEAGE_DB_ENABLED", "false").lower() == "true"
        
        if self.enabled:
            self._connect()
        else:
            print("ℹ️ Banco Lineage desativado via configuração")
            
        self._initialized = True

    def _connect(self):
        try:
            user = os.getenv("LINEAGE_DB_USER")
            password = os.getenv("LINEAGE_DB_PASSWORD")
            host = os.getenv("LINEAGE_DB_HOST")
            port = os.getenv("LINEAGE_DB_PORT", "3306")
            dbname = os.getenv("LINEAGE_DB_NAME")

            url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{dbname}"
            self.engine = create_engine(url, echo=False, pool_pre_ping=True)
            print("✅ Conectado ao banco Lineage com SQLAlchemy")
        except Exception as e:
            print(f"❌ Falha ao conectar ao banco Lineage: {e}")
            self.engine = None

    def _normalize_params(self, query: str, params: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        new_params = {}
        for key, val in params.items():
            if isinstance(val, list):
                placeholders = []
                for i, item in enumerate(val):
                    new_key = f"{key}_{i}"
                    placeholders.append(f":{new_key}")
                    new_params[new_key] = item
                query = query.replace(f":{key}", f"({', '.join(placeholders)})")
            else:
                new_params[key] = val
        return query, new_params

    def _get_cache(self, query: str, params: Tuple) -> Optional[List[Dict]]:
        key = (query, params)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_ttl:
                print("⚡ Consulta retornada do cache")
                return data
            else:
                del self.cache[key]
        return None

    def _set_cache(self, query: str, params: Tuple, data: List[Dict]):
        self.cache[(query, params)] = (data, time.time())

    def _safe_execute_read(self, query: str, params: Dict[str, Any]) -> Optional[Result]:
        if not self.enabled:
            return None
        if not self.engine:
            print("⚠️ Sem conexão com o banco")
            return None
        try:
            query, normalized_params = self._normalize_params(query, params)
            with self.engine.connect() as conn:
                stmt = text(query)
                return conn.execute(stmt, normalized_params)
        except SQLAlchemyError as e:
            print(f"❌ Erro na execução: {e}")
            return None

    def _safe_execute_write(self, query: str, params: Dict[str, Any]) -> Optional[Result]:
        if not self.enabled:
            return None
        if not self.engine:
            print("⚠️ Sem conexão com o banco")
            return None
        try:
            query, normalized_params = self._normalize_params(query, params)
            with self.engine.begin() as conn:
                stmt = text(query)
                return conn.execute(stmt, normalized_params)
        except SQLAlchemyError as e:
            print(f"❌ Erro na execução: {e}")
            return None

    def is_connected(self) -> bool:
        if not self.enabled:
            return False
        if not self.engine:
            return False
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            print(f"❌ Conexão perdida: {e}")
            return False

    def select(self, query: str, params: Dict[str, Any] = {}, use_cache: bool = False) -> Optional[List[Dict]]:
        if not self.enabled:
            return []
        params = params or {}
        query_exp, params_exp = self._normalize_params(query, params)
        param_tuple = tuple(sorted(params_exp.items()))
        if use_cache:
            cached = self._get_cache(query_exp, param_tuple)
            if cached is not None:
                return cached

        result = self._safe_execute_read(query, params)
        if result is None:
            return []

        rows = result.mappings().all()
        if use_cache:
            self._set_cache(query_exp, param_tuple, rows)
        return rows

    def insert(self, query: str, params: Dict[str, Any] = {}) -> Optional[int]:
        if not self.enabled:
            return None
        return self._execute_and_get(query, params, "lastrowid")

    def update(self, query: str, params: Dict[str, Any] = {}) -> Optional[int]:
        if not self.enabled:
            return None
        affected_rows = self._execute_and_get(query, params, "rowcount")
        return affected_rows

    def delete(self, query: str, params: Dict[str, Any] = {}) -> Optional[int]:
        if not self.enabled:
            return None
        return self._execute_and_get(query, params, "rowcount")

    def _execute_and_get(self, query: str, params: Dict[str, Any], attr: str) -> Optional[int]:
        result = self._safe_execute_write(query, params)
        if result is None:
            return None
        return getattr(result, attr, None)

    def execute_raw(self, query: str, params: Dict[str, Any] = {}) -> bool:
        if not self.enabled:
            return False
        return self._safe_execute_write(query, params) is not None
    
    def get_table_columns(self, table_name: str) -> List[str]:
        """
        Retorna uma lista com os nomes das colunas da tabela.
        """
        if not self.enabled:
            return []
        if not self.engine:
            print("⚠️ Sem conexão com o banco")
            return []
        try:
            query = f"SHOW COLUMNS FROM `{table_name}`"
            with self.engine.connect() as conn:
                result = conn.execute(text(query))
                columns = [row[0] for row in result.fetchall()]
                return columns
        except SQLAlchemyError as e:
            print(f"❌ Erro ao buscar colunas da tabela {table_name}: {e}")
            return []

    def clear_cache(self):
        self.cache.clear()
