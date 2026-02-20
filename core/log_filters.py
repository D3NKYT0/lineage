"""
Filtros de logging para enriquecer os registros (ex.: request_id).
"""
import logging

from middlewares.request_id_middleware import get_request_id


class RequestIdFilter(logging.Filter):
    """
    Adiciona o request_id do contexto atual ao LogRecord.
    Assim os formatters podem usar %(request_id)s.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id() or ""
        return True
