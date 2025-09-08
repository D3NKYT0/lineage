from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from django.utils.translation import gettext_lazy as _
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)


class LineageAPIException(APIException):
    """Exceção base para a API do Lineage"""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    default_detail = _('Erro interno da API.')
    default_code = 'lineage_api_error'


class ServerUnavailableException(LineageAPIException):
    """Exceção para quando o servidor do jogo está indisponível"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Servidor do jogo indisponível.')
    default_code = 'server_unavailable'


class DataNotFoundException(LineageAPIException):
    """Exceção para quando dados não são encontrados"""
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = _('Dados não encontrados.')
    default_code = 'data_not_found'


class InvalidParameterException(LineageAPIException):
    """Exceção para parâmetros inválidos"""
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Parâmetro inválido.')
    default_code = 'invalid_parameter'


class RateLimitExceededException(LineageAPIException):
    """Exceção para quando o rate limit é excedido"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = _('Limite de requisições excedido.')
    default_code = 'rate_limit_exceeded'


class CacheException(LineageAPIException):
    """Exceção para problemas de cache"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = _('Erro no sistema de cache.')
    default_code = 'cache_error'


def custom_exception_handler(exc, context):
    """
    Handler customizado para exceções da API
    """
    # Chama o handler padrão primeiro
    response = exception_handler(exc, context)
    
    if response is not None:
        # Adiciona informações extras à resposta
        response.data = {
            'error': {
                'type': exc.__class__.__name__,
                'message': response.data.get('detail', str(exc)),
                'code': getattr(exc, 'default_code', 'unknown_error'),
                'status_code': response.status_code,
            },
            'timestamp': timezone.now().isoformat(),
            'path': context['request'].path,
            'method': context['request'].method,
        }
        
        # Log do erro
        logger.error(
            f"API Error: {exc.__class__.__name__} - {response.data['error']['message']}",
            extra={
                'status_code': response.status_code,
                'path': context['request'].path,
                'method': context['request'].method,
                'user': getattr(context['request'], 'user', None),
                'ip': get_client_ip(context['request']),
            }
        )
    
    return response


def get_client_ip(request):
    """Obtém o IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


class APIErrorResponse:
    """Classe para criar respostas de erro padronizadas"""
    
    @staticmethod
    def not_found(message="Recurso não encontrado", code="not_found"):
        return Response({
            'error': {
                'type': 'DataNotFoundException',
                'message': message,
                'code': code,
                'status_code': 404,
            },
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def bad_request(message="Requisição inválida", code="bad_request"):
        return Response({
            'error': {
                'type': 'InvalidParameterException',
                'message': message,
                'code': code,
                'status_code': 400,
            },
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def server_error(message="Erro interno do servidor", code="server_error"):
        return Response({
            'error': {
                'type': 'LineageAPIException',
                'message': message,
                'code': code,
                'status_code': 500,
            },
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @staticmethod
    def service_unavailable(message="Serviço indisponível", code="service_unavailable"):
        return Response({
            'error': {
                'type': 'ServerUnavailableException',
                'message': message,
                'code': code,
                'status_code': 503,
            },
            'timestamp': timezone.now().isoformat(),
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE) 