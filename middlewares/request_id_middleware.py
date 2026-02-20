"""
Middleware que atribui um ID único a cada request para rastreio em logs.
Use em todos os log calls; o formatter inclui request_id quando disponível.
"""
import logging
import uuid

import threading

# Thread-local para armazenar request_id (usado pelo filter de logging)
_request_id_local = threading.local()


def get_request_id():
    """Retorna o request_id do contexto atual (request em andamento) ou None."""
    return getattr(_request_id_local, "request_id", None)


def set_request_id(value):
    """Define o request_id no contexto atual (usado pelo middleware)."""
    _request_id_local.request_id = value


def clear_request_id():
    """Remove o request_id do contexto (chamado no final do request)."""
    if hasattr(_request_id_local, "request_id"):
        del _request_id_local.request_id


class RequestIdMiddleware:
    """
    Adiciona request_id ao request e ao contexto de logging.
    Coloque cedo na pilha de middlewares (ex.: após SessionMiddleware).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Usa header se existir (ex.: load balancer), senão gera um
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())[:16]
        request.request_id = request_id
        set_request_id(request_id)
        try:
            response = self.get_response(request)
            if hasattr(response, "headers"):
                response["X-Request-ID"] = request_id
            return response
        finally:
            clear_request_id()
