import time
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LoginAttemptsMiddleware:
    """
    Middleware para rastrear tentativas de login e gerenciar captcha
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Verifica se é uma tentativa de login ANTES de processar
        is_login_attempt = request.method == 'POST' and request.path.endswith('/login/')
        
        # Processa a requisição
        response = self.get_response(request)
        
        # Gerencia tentativas de login APÓS processar
        if is_login_attempt:
            self._handle_login_attempt(request, response)
        
        return response
    
    def _handle_login_attempt(self, request, response):
        """Gerencia tentativas de login"""
        # Só incrementa tentativas se a resposta não for um redirecionamento bem-sucedido
        # O reset das tentativas será feito na view quando o login for bem-sucedido
        if response.status_code != 302:
            client_ip = self._get_client_ip(request)
            cache_key = f"login_attempts_{client_ip}"
            
            # Verifica se há mensagens de erro específicas de suspensão ou conta inativa
            # Se houver, não incrementa as tentativas para não interferir com a mensagem
            has_suspension_error = False
            
            # Verifica no context_data da resposta
            if hasattr(response, 'context_data') and response.context_data:
                form = response.context_data.get('form')
                if form and hasattr(form, 'non_field_errors'):
                    non_field_errors = form.non_field_errors()
                    if non_field_errors:
                        for error in non_field_errors:
                            error_str = str(error)
                            # Detecta mensagens de suspensão (🔴 🟡) ou conta inativa
                            if ("🔴" in error_str or "🟡" in error_str or 
                                "não está activa" in error_str or 
                                "não está ativa" in error_str or
                                "suspensa" in error_str.lower() or
                                "banida" in error_str.lower() or
                                "desativada" in error_str.lower()):
                                has_suspension_error = True
                                logger.info(f"Detectada mensagem de conta inativa para IP {client_ip}, não incrementando tentativas")
                                break
            
            # Verifica também no conteúdo da resposta para casos onde context_data não está disponível
            if not has_suspension_error and hasattr(response, 'content'):
                content_str = str(response.content)
                if ("🔴" in content_str or "🟡" in content_str or 
                    "não está activa" in content_str or 
                    "não está ativa" in content_str or
                    "suspensa" in content_str.lower() or
                    "banida" in content_str.lower() or
                    "desativada" in content_str.lower()):
                    has_suspension_error = True
                    logger.info(f"Detectada mensagem de conta inativa no conteúdo para IP {client_ip}, não incrementando tentativas")
            
            # Só incrementa tentativas se não for um erro de suspensão/conta inativa
            if not has_suspension_error:
                # Obtém tentativas atuais e incrementa
                attempts = cache.get(cache_key, 1) + 1
                cache.set(cache_key, attempts, 3600)  # Expira em 1 hora
                logger.warning(f"Tentativa de login falhou para IP {client_ip}, tentativa {attempts}")
                
                # Se chegou ao limite, força a próxima requisição a mostrar captcha
                if attempts >= getattr(settings, 'LOGIN_MAX_ATTEMPTS', 3):
                    logger.info(f"IP {client_ip} atingiu limite de tentativas ({attempts}). Captcha será exigido na próxima tentativa.")
            else:
                logger.info(f"Tentativa de login com conta inativa para IP {client_ip}, não incrementando contador")
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_login_attempts(request):
        """Retorna o número de tentativas de login para o IP"""
        client_ip = LoginAttemptsMiddleware._get_client_ip_static(request)
        cache_key = f"login_attempts_{client_ip}"
        return cache.get(cache_key, 0)
    
    @staticmethod
    def _get_client_ip_static(request):
        """Versão estática para obter IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def requires_captcha(request):
        """Verifica se o captcha é necessário"""
        attempts = LoginAttemptsMiddleware.get_login_attempts(request)
        max_attempts = getattr(settings, 'LOGIN_MAX_ATTEMPTS', 3)
        # Captcha é necessário quando atingiu ou excedeu o número máximo de tentativas
        # Ou seja, após 3 tentativas falhadas, a 4ª tentativa deve ter captcha
        requires = attempts >= max_attempts
        logger.debug(f"Verificando captcha: {attempts} tentativas >= {max_attempts} = {requires}")
        return requires
    
    @staticmethod
    def reset_attempts(request):
        """Reseta as tentativas de login"""
        client_ip = LoginAttemptsMiddleware._get_client_ip_static(request)
        cache_key = f"login_attempts_{client_ip}"
        cache.delete(cache_key)
        logger.info(f"Tentativas de login resetadas para IP {client_ip}") 