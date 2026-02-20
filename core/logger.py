"""
Configuração central de logging do projeto PDL.
- Formatters com timestamp ISO, nível, módulo e request_id (quando disponível).
- Handlers por nível com rotação; console com formato legível.
- Use logging.getLogger(__name__) e, quando fizer sentido, core.log_utils para mensagens estruturadas.
"""
import os
import sys
import json
import logging
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    """
    Formatter que gera uma linha JSON por log, ideal para agregadores (CloudWatch, ELK, etc).
    Inclui request_id quando disponível.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if getattr(record, "request_id", None):
            log_data["request_id"] = record.request_id
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        # Incluir extras comuns sem quebrar
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "exc_info", "message", "thread", "threadName",
                "request_id", "taskName", "msg", "exc_text",
            ) and value is not None:
                try:
                    log_data[key] = value
                except Exception:
                    pass
        return json.dumps(log_data, ensure_ascii=False)


LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        # Legado (mantido para compatibilidade)
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        # Novo: contexto claro + request_id
        "verbose_ctx": {
            "format": "[{asctime}] {levelname:8} | {name} | req={request_id} | {message}",
            "style": "{",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "verbose_ctx_exception": {
            "format": "[{asctime}] {levelname:8} | {name} | req={request_id} | {message}\n{exc_text}",
            "style": "{",
            "datefmt": "%Y-%m-%dT%H:%M:%S",
        },
        "console_ctx": {
            "format": "[{asctime}] {levelname:8} {name} req={request_id} {message}",
            "style": "{",
            "datefmt": "%H:%M:%S",
        },
        "json": {
            "()": "core.logger.JsonFormatter",
        },
    },

    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "request_id": {
            "()": "core.log_filters.RequestIdFilter",
        },
    },

    "handlers": {
        "file_debug": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "debug.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose_ctx",
            "filters": ["require_debug_false", "request_id"],
        },
        "file_info": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "info.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose_ctx",
            "filters": ["require_debug_false", "request_id"],
        },
        "file_warning": {
            "level": "WARNING",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "warning.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose_ctx",
            "filters": ["require_debug_false", "request_id"],
        },
        "file_error": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "error.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose_ctx",
            "filters": ["require_debug_false", "request_id"],
        },
        "file_critical": {
            "level": "CRITICAL",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "critical.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose_ctx",
            "filters": ["require_debug_false", "request_id"],
        },
        "file_wallet": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(LOG_DIR, "wallet.log"),
            "maxBytes": 1024 * 1024 * 5,
            "backupCount": 7,
            "formatter": "verbose_ctx",
            "filters": ["require_debug_false", "request_id"],
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "console_ctx",
            "stream": sys.stdout,
            "filters": ["request_id"],
        },
    },

    "loggers": {
        "django": {
            "handlers": ["file_info", "file_warning", "file_error", "file_critical", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["file_info", "file_warning", "file_error", "file_critical", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "celery": {
            "handlers": ["file_debug", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "apps.lineage.wallet": {
            "handlers": ["file_wallet", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Logger raiz: módulos que usam getLogger(__name__) sem logger específico usam estes handlers
LOGGING["root"] = {
    "handlers": ["file_info", "file_warning", "file_error", "file_critical", "console"],
    "level": "INFO",
}
