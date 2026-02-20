"""
Helpers para logs estruturados e consistentes no projeto.
Use junto com logging.getLogger(__name__) para manter contexto (módulo) e opcionalmente
padronizar mensagens por ação/resultado.

Exemplo de uso:
    from core.log_utils import get_logger, log_action

    logger = get_logger(__name__)
    log_action(logger, "login", "tentativa", username=username)
    log_action(logger, "login", "sucesso", username=user.username)
    log_action(logger, "login", "falha", reason="credenciais_invalidas", username=username)
"""
import logging
from typing import Any, Optional


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger com o nome do módulo (use __name__).
    Equivalente a logging.getLogger(__name__), documentado como padrão do projeto.
    """
    return logging.getLogger(name)


def _fmt_extra(**kwargs: Any) -> str:
    """Formata extras como key=value para inclusão na mensagem."""
    parts = [f"{k}={v}" for k, v in kwargs.items() if v is not None]
    return " | ".join(parts) if parts else ""


def log_action(
    logger: logging.Logger,
    action: str,
    status: str,
    message: Optional[str] = None,
    level: int = logging.INFO,
    exc_info: bool = False,
    **extra: Any,
) -> None:
    """
    Registra uma ação com formato consistente: [ação] status [mensagem] [extras].

    Uso:
        log_action(logger, "login", "sucesso", username=user.username)
        log_action(logger, "transfer", "erro", message="saldo insuficiente", level=logging.ERROR, account_id=123)
    """
    extra_str = _fmt_extra(**extra)
    parts = [f"[{action}]", status]
    if message:
        parts.append(message)
    if extra_str:
        parts.append(extra_str)
    log_message = " ".join(parts)
    logger.log(level, log_message, exc_info=exc_info)
    # Telemetria: contador de eventos de negócio (se TELEMETRY_ENABLED)
    try:
        from django.conf import settings
        if getattr(settings, "TELEMETRY_ENABLED", False):
            from core.telemetry import record_business_event
            record_business_event(action, status)
    except Exception:
        pass


def log_request(
    logger: logging.Logger,
    method: str,
    path: str,
    status: str = "inicio",
    user: Optional[str] = None,
    status_code: Optional[int] = None,
    duration_ms: Optional[float] = None,
    **extra: Any,
) -> None:
    """
    Log focado em request HTTP: método, path, status (inicio/sucesso/erro), user, status_code, duração.
    """
    extra_dict = {"method": method, "path": path, **extra}
    if user is not None:
        extra_dict["user"] = user
    if status_code is not None:
        extra_dict["status_code"] = status_code
    if duration_ms is not None:
        extra_dict["duration_ms"] = round(duration_ms, 2)
    log_action(logger, "request", status, **extra_dict)
