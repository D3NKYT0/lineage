import importlib
import os
from dotenv import load_dotenv

load_dotenv()

def get_query_class(class_name: str, env_var: str = "LINEAGE_QUERY_MODULE", default_module: str = "dreamv3"):
    """
    Importa dinamicamente uma classe de um módulo baseado em variável de ambiente.

    :param class_name: Nome da classe a ser importada (ex: "LineageStats")
    :param env_var: Nome da variável de ambiente (default: LINEAGE_QUERY_MODULE)
    :param default_module: Valor padrão caso a env var não esteja setada
    :return: Classe importada
    """
    module_suffix = os.getenv(env_var, default_module)
    module_path = f"apps.lineage.server.querys.query_{module_suffix}"

    try:
        mod = importlib.import_module(module_path)
        cls = getattr(mod, class_name)
        return cls
    except (ModuleNotFoundError, AttributeError) as e:
        raise ImportError(f"Não foi possível importar {class_name} de {module_path}: {e}")
