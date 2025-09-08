import logging

from django_ratelimit.core import is_ratelimited, get_usage
from django.http import JsonResponse
from utils.urls_rate_limits import URL_RATE_LIMITS_DICT


logger = logging.getLogger(__name__)


class RateLimitMiddleware:
    """
    Middleware para aplicar rate limiting em URLs específicas com configurações customizadas.
    """

    URL_RATE_LIMITS = URL_RATE_LIMITS_DICT

    def __init__(self, get_response):
        """
        Middleware de inicialização.
        Recebe get_response, necessário para os middlewares do Django.
        """
        self.get_response = get_response

    def __call__(self, request):
        """
        Método chamado para processar as requisições.
        """
        response = self.process_request(request)
        if response:
            return response

        # Continue com o fluxo normal
        return self.get_response(request)

    def process_request(self, request):
        logger.debug("Middleware foi chamada para verificar rate limit")
        
        for path, config in self.URL_RATE_LIMITS.items():
            logger.debug(f"Checking path {request.path} against {path}")
            if request.path.rstrip('/') == path.rstrip('/'):

                method = config.get("method", "GET")

                was_limited = is_ratelimited(
                    request=request,
                    group=config["group"],
                    key=config["key"],
                    rate=config["rate"],
                    method=method,
                    increment=True,
                )

                if was_limited:
                    logger.warning(f"Rate limit exceeded for path {path}")

                    usage = get_usage(
                        request=request,
                        group=config["group"],
                        key=config["key"],
                        rate=config["rate"],
                        method=method,
                        increment=False
                    )

                    reset_time = usage['time_left']

                    return JsonResponse(
                        {"error": "Rate limit exceeded", "retry_after": reset_time},
                        status=429
                    )
        return None
