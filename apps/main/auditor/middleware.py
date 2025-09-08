import logging
from functools import reduce
from operator import add
from time import time
import threading

from django.conf import settings
from django.db import IntegrityError, DataError, connection, transaction
from django.utils import timezone
from django.http.request import RawPostDataException

from .models import Auditor
from python_ipware import IpWare

logger = logging.getLogger(__name__)
ipw = IpWare(precedence=("X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"))

class AuditorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.AUDITOR_MIDDLEWARE_ENABLE = getattr(settings, "AUDITOR_MIDDLEWARE_ENABLE", False)
        self.AUDITOR_MIDDLEWARE_RESTRICT_PATHS = getattr(settings, "AUDITOR_MIDDLEWARE_RESTRICT_PATHS", [])
        self.AUDITOR_MIDDLEWARE_CONTENT = getattr(settings, "DEBUG", False)
        # Adiciona lock para evitar concorrência
        self._save_lock = threading.Lock()

    def __call__(self, request):
        if not self.AUDITOR_MIDDLEWARE_ENABLE:
            response = self.get_response(request)
            logger.info('Auditor Middleware is disabled!')
            return response
        
        # Ignora requisições para arquivos estáticos e mídia
        if self._should_skip_audit(request.path):
            response = self.get_response(request)
            return response
        
        if '/app/auditor/' in request.path:
            # isso evita que o auditor audite ele mesmo.
            response = self.get_response(request)
            return response

        if self.AUDITOR_MIDDLEWARE_RESTRICT_PATHS:
            found = any(request.path.startswith(path) for path in self.AUDITOR_MIDDLEWARE_RESTRICT_PATHS)
            if not found:
                response = self.get_response(request)
                return response

        previous_connections = len(connection.queries)
        start_time = time()

        # Save the raw body data before it's potentially read
        try:
            raw_body = request.body
        except RawPostDataException:
            raw_body = None

        response = self.get_response(request)

        s = {
            'date': timezone.now(),
            'path': request.path,
            'total_time': time() - start_time,
            'total_queries': len(connection.queries) - previous_connections,
        }

        if s['total_queries'] > 0:
            s['db_time'] = reduce(add, [float(q['time']) for q in connection.queries[previous_connections:]])
        else:
            s['db_time'] = 0.0

        s['python_time'] = s['total_time'] - s['db_time']
        ip, s['proxy_verified'] = ipw.get_client_ip(meta=request.META)
        s['ip'] = str(ip) if ip is not None else request.META.get('REMOTE_ADDR')
        s['method'] = request.method
        s['user_agent'] = request.headers.get("User-Agent", "")
        s['host'] = request.get_host()
        s['port'] = request.get_port()
        s['content_type'] = request.content_type

        if s['method'] == "POST" and s['content_type'] == "application/json" and raw_body:
            s['body'] = raw_body.decode()
        else:
            s['body'] = None

        s['response_content'] = "DISABLE"
        s['response_status_code'] = getattr(response, 'status_code', None)

        # Salva os dados de auditoria de forma assíncrona e segura
        self._save_audit_data_async(s)

        return response

    def _should_skip_audit(self, path):
        """Verifica se deve pular a auditoria para este caminho"""
        skip_patterns = [
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
            '/admin/jsi18n/',
            '/__debug__/',
        ]
        return any(path.startswith(pattern) for pattern in skip_patterns)

    def _save_audit_data_async(self, audit_data):
        """Salva dados de auditoria de forma assíncrona e segura"""
        try:
            # Usa lock para evitar concorrência
            with self._save_lock:
                # Garantir que todos os campos obrigatórios estão presentes
                required_fields = ['date', 'path', 'total_time', 'total_queries', 'db_time', 'python_time', 'ip', 'method', 'user_agent', 'host', 'port', 'content_type', 'response_content', 'response_status_code']
                missing_fields = [field for field in required_fields if field not in audit_data or audit_data[field] is None]

                if missing_fields:
                    logger.error(f"Missing required fields: {missing_fields}. Unable to save event data: {audit_data}")
                    return

                # Tenta salvar com timeout e retry
                self._save_with_retry(audit_data)

        except Exception as e:
            logger.error(f"Unexpected error in audit save: {e}. Event data: {audit_data}")

    def _save_with_retry(self, audit_data, max_retries=3, retry_delay=0.1):
        """Salva com retry em caso de erro de banco bloqueado"""
        for attempt in range(max_retries):
            try:
                with transaction.atomic():
                    event = Auditor(**audit_data)
                    event.save()
                return  # Sucesso, sai da função
                
            except IntegrityError as e:
                logger.warning(f"IntegrityError (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"IntegrityError: Error saving statistics to the database. Error: {e}. Event data: {audit_data}")
                    
            except DataError as e:
                logger.warning(f"DataError (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"DataError: Error saving statistics to the database. Error: {e}. Event data: {audit_data}")
                    
            except Exception as e:
                if "database is locked" in str(e).lower():
                    logger.warning(f"Database locked (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(retry_delay * (attempt + 1))  # Backoff exponencial
                        continue
                logger.error(f"Error saving statistics to the database. Error: {e}. Event data: {audit_data}")
                break
