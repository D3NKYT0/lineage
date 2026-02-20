"""
Telemetria do projeto PDL: métricas Prometheus para requests HTTP e eventos de negócio.

- Requisições: contagem e duração por método, path (normalizado) e status.
- Eventos de negócio: contadores por ação/status (opcional, integração com log_action).

Ative com TELEMETRY_ENABLED=True. Endpoint de scrape: TELEMETRY_METRICS_PATH (ex.: /internal/metrics).
"""
import re
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Evita importar prometheus_client se telemetria estiver desativada
_metrics = None
_REGISTRY = None


def _get_registry():
    global _REGISTRY
    if _REGISTRY is None:
        try:
            from prometheus_client import REGISTRY as _REGISTRY_MOD
            _REGISTRY = _REGISTRY_MOD
        except ImportError:
            _REGISTRY = False
    return _REGISTRY


def _get_metrics():
    """Lazy init dos métricos Prometheus (só quando telemetria está ativa e lib disponível)."""
    global _metrics
    if _metrics is not None:
        return _metrics
    try:
        from prometheus_client import Counter, Histogram
        ns = "pdl"
        _metrics = {
            "http_requests_total": Counter(
                "http_requests_total",
                "Total de requisições HTTP",
                ["method", "path", "status_class"],
                namespace=ns,
            ),
            "http_request_duration_seconds": Histogram(
                "http_request_duration_seconds",
                "Duração das requisições HTTP em segundos",
                ["method", "path"],
                namespace=ns,
                buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            ),
            "business_events_total": Counter(
                "business_events_total",
                "Eventos de negócio (wallet, payment, social, etc.)",
                ["action", "status"],
                namespace=ns,
            ),
        }
    except ImportError:
        _metrics = {}
        logger.debug("prometheus_client não disponível; telemetria de métricas desativada.")
    return _metrics


def normalize_path(path: str, max_segments: int = 4) -> str:
    """
    Reduz cardinalidade do path: /wallet/transfer/123/ -> /wallet/transfer/{id}/,
    /app/shop/42/item -> /app/shop/{id}/item.
    """
    if not path or path == "/":
        return "/"
    path = path.rstrip("/") or "/"
    parts = [p for p in path.split("/") if p]
    if len(parts) <= max_segments:
        # Se tem número no último segmento, normaliza
        if parts and re.match(r"^\d+$", parts[-1]):
            return "/" + "/".join(parts[:-1]) + "/{id}"
        return "/" + "/".join(parts)
    # Muitos segmentos: mantém os primeiros e agrupa o resto
    head = parts[: max_segments - 1]
    return "/" + "/".join(head) + "/..."


def record_request(
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
    path_normalized: Optional[str] = None,
) -> None:
    """Registra uma requisição HTTP para as métricas Prometheus."""
    metrics = _get_metrics()
    if not metrics:
        return
    path_norm = path_normalized or normalize_path(path)
    status_class = f"{status_code // 100}xx"
    try:
        metrics["http_requests_total"].labels(
            method=method.upper(),
            path=path_norm,
            status_class=status_class,
        ).inc()
        metrics["http_request_duration_seconds"].labels(
            method=method.upper(),
            path=path_norm,
        ).observe(duration_seconds)
    except Exception as e:
        logger.debug("Telemetria record_request: %s", e)


def record_business_event(action: str, status: str) -> None:
    """Incrementa contador de evento de negócio (ex.: wallet_transfer_p2p, sucesso)."""
    metrics = _get_metrics()
    if not metrics or "business_events_total" not in metrics:
        return
    try:
        metrics["business_events_total"].labels(action=action, status=status).inc()
    except Exception as e:
        logger.debug("Telemetria record_business_event: %s", e)


def get_metrics_content() -> Optional[bytes]:
    """Gera o corpo da resposta no formato Prometheus (text/plain). Retorna None se indisponível."""
    if _get_registry() is False:
        return None
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        return generate_latest(_get_registry())
    except Exception as e:
        logger.warning("Falha ao gerar métricas Prometheus: %s", e)
        return None


def get_content_type() -> str:
    try:
        from prometheus_client import CONTENT_TYPE_LATEST
        return CONTENT_TYPE_LATEST
    except ImportError:
        return "text/plain; charset=utf-8"
