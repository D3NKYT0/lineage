import os
from utils.dynamic_import import get_query_class
from sqlalchemy.exc import SQLAlchemyError
from pymysql.err import OperationalError

# Verifica se o banco Lineage está habilitado
if os.getenv("LINEAGE_DB_ENABLED", "false").lower() == "true":
    try:
        LineageAccount = get_query_class("LineageAccount")
        LineageAccount.ensure_columns()
    except (SQLAlchemyError, OperationalError) as e:
        print(f"⚠️ Não foi possível conectar ao banco do Lineage 2: {e}")
        print("ℹ️ O sistema continuará funcionando normalmente, mas algumas funcionalidades podem estar indisponíveis.")
    except Exception as e:
        print(f"⚠️ Erro inesperado ao verificar colunas do banco: {e}")
        print("ℹ️ O sistema continuará funcionando normalmente, mas algumas funcionalidades podem estar indisponíveis.")
else:
    print("ℹ️ Banco Lineage desativado via configuração - pulando verificação de colunas")
