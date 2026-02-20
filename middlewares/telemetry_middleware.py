"""
Middleware de telemetria: registra duração e status de cada request nas métricas Prometheus.
Só atua quando TELEMETRY_ENABLED=True. URLs em TELEMETRY_EXCLUDE_PATHS são ignoradas.
"""
import time
import logging

logger = logging.getLogger(__name__)


class TelemetryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.conf import settings
        if not getattr(settings, "TELEMETRY_ENABLED", False):
            return self.get_response(request)

        exclude_paths = getattr(settings, "TELEMETRY_EXCLUDE_PATHS", [])
        path = request.path_info or request.path
        if any(path.startswith(p) for p in exclude_paths):
            return self.get_response(request)

        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start
        status_code = getattr(response, "status_code", 500)

        try:
            from core.telemetry import record_request
            record_request(
                method=request.method,
                path=path,
                status_code=status_code,
                duration_seconds=duration,
            )
        except Exception as e:
            logger.debug("Telemetria middleware: %s", e)

        return response
