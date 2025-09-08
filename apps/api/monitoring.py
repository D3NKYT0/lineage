import time
import logging
from django.utils import timezone
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from functools import wraps
import json

logger = logging.getLogger(__name__)


class APIMetrics:
    """Sistema de métricas para a API"""
    
    @staticmethod
    def record_request(request, response, duration):
        """Registra métricas de uma requisição"""
        try:
            # Métricas básicas
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'duration_ms': round(duration * 1000, 2),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'ip': APIMetrics.get_client_ip(request),
                'user_id': getattr(request.user, 'id', None) if request.user.is_authenticated else None,
            }
            
            # Armazena no cache para análise
            cache_key = f"api_metrics_{timezone.now().strftime('%Y%m%d_%H')}"
            existing_metrics = cache.get(cache_key, [])
            existing_metrics.append(metrics)
            
            # Mantém apenas as últimas 1000 métricas por hora
            if len(existing_metrics) > 1000:
                existing_metrics = existing_metrics[-1000:]
            
            cache.set(cache_key, existing_metrics, 3600)  # 1 hora
            
            # Log para análise
            logger.info(
                f"API Request: {request.method} {request.path} - {response.status_code} - {duration:.3f}s",
                extra=metrics
            )
            
        except Exception as e:
            logger.error(f"Error recording API metrics: {e}")
    
    @staticmethod
    def get_client_ip(request):
        """Obtém o IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_hourly_stats():
        """Obtém estatísticas da última hora"""
        try:
            cache_key = f"api_metrics_{timezone.now().strftime('%Y%m%d_%H')}"
            metrics = cache.get(cache_key, [])
            
            if not metrics:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'status_codes': {},
                    'endpoints': {},
                    'error_rate': 0,
                }
            
            total_requests = len(metrics)
            total_duration = sum(m['duration_ms'] for m in metrics)
            avg_response_time = total_duration / total_requests if total_requests > 0 else 0
            
            # Conta códigos de status
            status_codes = {}
            for m in metrics:
                status = m['status_code']
                status_codes[status] = status_codes.get(status, 0) + 1
            
            # Conta endpoints
            endpoints = {}
            for m in metrics:
                path = m['path']
                endpoints[path] = endpoints.get(path, 0) + 1
            
            # Calcula taxa de erro
            error_count = sum(1 for m in metrics if m['status_code'] >= 400)
            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 2),
                'status_codes': status_codes,
                'endpoints': endpoints,
                'error_rate': round(error_rate, 2),
                'period': 'last_hour',
            }
            
        except Exception as e:
            logger.error(f"Error getting hourly stats: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def get_daily_stats():
        """Obtém estatísticas do dia atual"""
        try:
            # Busca métricas de todas as horas do dia
            daily_metrics = []
            for hour in range(24):
                cache_key = f"api_metrics_{timezone.now().strftime('%Y%m%d')}_{hour:02d}"
                metrics = cache.get(cache_key, [])
                daily_metrics.extend(metrics)
            
            if not daily_metrics:
                return {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'status_codes': {},
                    'endpoints': {},
                    'error_rate': 0,
                }
            
            total_requests = len(daily_metrics)
            total_duration = sum(m['duration_ms'] for m in daily_metrics)
            avg_response_time = total_duration / total_requests if total_requests > 0 else 0
            
            # Conta códigos de status
            status_codes = {}
            for m in daily_metrics:
                status = m['status_code']
                status_codes[status] = status_codes.get(status, 0) + 1
            
            # Conta endpoints
            endpoints = {}
            for m in daily_metrics:
                path = m['path']
                endpoints[path] = endpoints.get(path, 0) + 1
            
            # Calcula taxa de erro
            error_count = sum(1 for m in daily_metrics if m['status_code'] >= 400)
            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'avg_response_time': round(avg_response_time, 2),
                'status_codes': status_codes,
                'endpoints': endpoints,
                'error_rate': round(error_rate, 2),
                'period': 'today',
            }
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {'error': str(e)}


def monitor_api_request(func):
    """Decorator para monitorar requisições da API"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        # Extrai request dos argumentos
        request = None
        for arg in args:
            if hasattr(arg, 'method') and hasattr(arg, 'path'):
                request = arg
                break
        
        try:
            response = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if request:
                APIMetrics.record_request(request, response, duration)
            
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            
            # Cria uma resposta de erro para métricas
            error_response = Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
            if request:
                APIMetrics.record_request(request, error_response, duration)
            
            raise
    
    return wrapper


class HealthCheck:
    """Sistema de health check para a API"""
    
    @staticmethod
    def check_database():
        """Verifica saúde do banco de dados"""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return {'status': 'healthy', 'message': 'Database connection OK'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Database error: {str(e)}'}
    
    @staticmethod
    def check_cache():
        """Verifica saúde do cache"""
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            if result == 'ok':
                return {'status': 'healthy', 'message': 'Cache connection OK'}
            else:
                return {'status': 'unhealthy', 'message': 'Cache read/write failed'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Cache error: {str(e)}'}
    
    @staticmethod
    def check_game_server():
        """Verifica saúde do servidor do jogo"""
        try:
            from utils.dynamic_import import get_query_class
            LineageStats = get_query_class("LineageStats")
            
            # Tenta uma consulta simples
            data = LineageStats.players_online()
            if data is not None:
                return {'status': 'healthy', 'message': 'Game server connection OK'}
            else:
                return {'status': 'unhealthy', 'message': 'Game server returned no data'}
        except Exception as e:
            return {'status': 'unhealthy', 'message': f'Game server error: {str(e)}'}
    
    @staticmethod
    def full_health_check():
        """Executa verificação completa de saúde"""
        checks = {
            'database': HealthCheck.check_database(),
            'cache': HealthCheck.check_cache(),
            'game_server': HealthCheck.check_game_server(),
        }
        
        overall_status = 'healthy'
        if any(check['status'] == 'unhealthy' for check in checks.values()):
            overall_status = 'unhealthy'
        
        return {
            'status': overall_status,
            'timestamp': timezone.now().isoformat(),
            'checks': checks,
        }


class APIPerformance:
    """Monitoramento de performance da API"""
    
    @staticmethod
    def get_slow_queries(limit=10):
        """Obtém as queries mais lentas"""
        try:
            # Busca métricas das últimas 24 horas
            slow_queries = []
            for hour in range(24):
                cache_key = f"api_metrics_{timezone.now().strftime('%Y%m%d')}_{hour:02d}"
                metrics = cache.get(cache_key, [])
                
                # Filtra queries lentas (> 1 segundo)
                slow = [m for m in metrics if m['duration_ms'] > 1000]
                slow_queries.extend(slow)
            
            # Ordena por duração e retorna as mais lentas
            slow_queries.sort(key=lambda x: x['duration_ms'], reverse=True)
            return slow_queries[:limit]
            
        except Exception as e:
            logger.error(f"Error getting slow queries: {e}")
            return []
    
    @staticmethod
    def get_endpoint_performance():
        """Obtém performance por endpoint"""
        try:
            # Busca métricas das últimas 24 horas
            endpoint_metrics = {}
            for hour in range(24):
                cache_key = f"api_metrics_{timezone.now().strftime('%Y%m%d')}_{hour:02d}"
                metrics = cache.get(cache_key, [])
                
                for m in metrics:
                    path = m['path']
                    if path not in endpoint_metrics:
                        endpoint_metrics[path] = {
                            'count': 0,
                            'total_duration': 0,
                            'errors': 0,
                        }
                    
                    endpoint_metrics[path]['count'] += 1
                    endpoint_metrics[path]['total_duration'] += m['duration_ms']
                    
                    if m['status_code'] >= 400:
                        endpoint_metrics[path]['errors'] += 1
            
            # Calcula médias
            for path, data in endpoint_metrics.items():
                data['avg_duration'] = round(data['total_duration'] / data['count'], 2)
                data['error_rate'] = round((data['errors'] / data['count']) * 100, 2)
            
            return endpoint_metrics
            
        except Exception as e:
            logger.error(f"Error getting endpoint performance: {e}")
            return {} 