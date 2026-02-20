"""
View que expõe métricas Prometheus no path configurado em TELEMETRY_METRICS_PATH.
Acesso: usuário staff ou requisição de localhost (para scrape do Prometheus).
"""
import logging
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden

logger = logging.getLogger(__name__)


def metrics_view(request):
    """Responde no formato Prometheus (text/plain)."""
    if not getattr(settings, "TELEMETRY_ENABLED", False):
        return HttpResponseForbidden("Telemetria desativada")

    # Permite: staff logado ou IP local (127.0.0.1, ::1) para Prometheus scrape
    allowed = False
    if request.user.is_authenticated and request.user.is_staff:
        allowed = True
    else:
        remote = request.META.get("REMOTE_ADDR") or ""
        if remote in ("127.0.0.1", "::1", "localhost"):
            allowed = True
        # Opcional: permitir por header secreto (ex.: X-Metrics-Token)
        token = request.headers.get("X-Metrics-Token", "")
        if token and token == getattr(settings, "TELEMETRY_SCRAPE_TOKEN", ""):
            allowed = True

    if not allowed:
        return HttpResponseForbidden("Acesso negado")

    from core.telemetry import get_metrics_content, get_content_type
    content = get_metrics_content()
    if content is None:
        return HttpResponse("# Métricas indisponíveis\n", content_type="text/plain")
    return HttpResponse(content, content_type=get_content_type())
