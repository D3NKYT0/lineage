"""
Middleware para registrar métricas da API (APIMetrics).
Registra cada requisição /api/ para alimentar a aba de métricas do PWA.
"""
import time
import logging

logger = logging.getLogger(__name__)


class APIMetricsMiddleware:
    """Registra métricas de requisições /api/ para APIMetrics."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or request.path
        if not path.startswith("/api/"):
            return self.get_response(request)

        start = time.perf_counter()
        response = self.get_response(request)
        duration = time.perf_counter() - start

        try:
            from apps.api.monitoring import APIMetrics
            APIMetrics.record_request(request, response, duration)
        except Exception as e:
            logger.debug("APIMetricsMiddleware: %s", e)

        return response
