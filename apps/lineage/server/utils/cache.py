from django.core.cache import cache
import hashlib
import json
from sqlalchemy.engine import RowMapping


def convert_rowmapping_to_dict(obj):
    if isinstance(obj, list):
        return [dict(row) for row in obj]
    elif isinstance(obj, RowMapping):
        return dict(obj)
    return obj


def cache_lineage_result(timeout=300, use_cache=True):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Se o cache não deve ser usado, execute a função normalmente
            if not use_cache:
                result = func(*args, **kwargs)
                result_converted = convert_rowmapping_to_dict(result)
                return result_converted
            
            # Gera uma chave única com base na função + argumentos
            key_base = f"{func.__module__}.{func.__name__}:{json.dumps(args)}:{json.dumps(kwargs)}"
            key = f"lineage_cache:{hashlib.md5(key_base.encode()).hexdigest()}"

            # Tenta pegar do cache
            cached = cache.get(key)
            if cached is not None:
                return cached

            # Se não tiver, executa e armazena no cache
            result = func(*args, **kwargs)

            # Converte o resultado antes de salvar e retornar
            result_converted = convert_rowmapping_to_dict(result)
            cache.set(key, result_converted, timeout=timeout)
            return result_converted
        return wrapper
    return decorator
