import logging
from django.utils import timezone
from django.db import transaction
from django.urls import resolve, Resolver404
from python_ipware import IpWare

logger = logging.getLogger(__name__)
ipw = IpWare(precedence=("X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"))


class PageViewMiddleware:
    """
    Middleware para rastrear visualizações de páginas pelos usuários.
    Registra visualizações para conquistas de exploração do site.
    """
    
    # URLs que devem ser rastreadas para conquistas
    TRACKED_PATTERNS = {
        # Feed Social
        'social_feed': ['/social/feed/'],
        
        # Tops
        'tops': [
            '/status/top-pvp/',
            '/status/top-pk/',
            '/status/top-adena/',
            '/status/top-clans/',
            '/status/top-level/',
            '/status/top-online/',
            '/status/top-raidboss/',
            '/status/top-custom/',
            '/public/tops/',
            '/public/tops/pvp/',
            '/public/tops/pk/',
            '/public/tops/adena/',
            '/public/tops/clans/',
            '/public/tops/level/',
            '/public/tops/online/',
            '/public/tops/olympiad/',
            '/public/tops/grandboss/',
            '/public/tops/raidboss/',
            '/public/tops/siege/',
        ],
        
        # Heroes
        'heroes': [
            '/status/olympiad-ranking/',
            '/status/olympiad-all-heroes/',
            '/status/olympiad-current-heroes/',
        ],
        
        # Castle Siege
        'siege': [
            '/status/siege-ranking/',
        ],
        
        # Boss Jewel Locations
        'boss_jewel': [
            '/status/boss-jewel-locations/',
        ],
        
        # Grand Boss Status
        'grandboss': [
            '/status/grandboss/',
        ],
    }
    
    # Padrões que devem ser ignorados
    IGNORE_PATTERNS = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/robots.txt',
        '/sitemap.xml',
        '/admin/',
        '/__debug__/',
        '/api/',
        '/decrypted-file/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processa a requisição normalmente
        response = self.get_response(request)
        
        # Só rastreia requisições GET bem-sucedidas
        if request.method == 'GET' and response.status_code == 200:
            # Verifica se deve ignorar esta URL
            if not self._should_track(request.path):
                return response
            
            # Rastreia a visualização de forma assíncrona
            self._track_page_view(request, response)
        
        return response
    
    def _should_track(self, path):
        """Verifica se a URL deve ser rastreada"""
        # Ignora padrões específicos
        if any(path.startswith(pattern) for pattern in self.IGNORE_PATTERNS):
            return False
        
        # Verifica se está em algum padrão rastreado
        for category, patterns in self.TRACKED_PATTERNS.items():
            if any(path.startswith(pattern) for pattern in patterns):
                return True
        
        return False
    
    def _track_page_view(self, request, response):
        """Rastreia a visualização da página"""
        try:
            # Só rastreia usuários autenticados
            if not request.user.is_authenticated:
                return
            
            # Obtém informações da URL
            url_path = request.path
            url_name = None
            view_name = None
            page_category = None
            
            # Tenta resolver o nome da URL
            try:
                resolver_match = resolve(url_path)
                url_name = resolver_match.url_name
                view_name = f"{resolver_match.func.__module__}.{resolver_match.func.__name__}"
            except Resolver404:
                pass
            
            # Determina a categoria da página
            page_category = self._get_page_category(url_path)
            
            # Obtém IP e User Agent
            ip, _ = ipw.get_client_ip(meta=request.META)
            ip_address = str(ip) if ip else None
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limita tamanho
            
            # Salva a visualização de forma assíncrona (não bloqueia a resposta)
            self._save_page_view_async(
                user=request.user,
                url_path=url_path,
                url_name=url_name,
                view_name=view_name,
                page_category=page_category,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
        except Exception as e:
            # Loga o erro mas não interrompe a requisição
            logger.error(f"Erro ao rastrear visualização de página: {e}", exc_info=True)
    
    def _get_page_category(self, path):
        """Determina a categoria da página baseada no caminho"""
        for category, patterns in self.TRACKED_PATTERNS.items():
            if any(path.startswith(pattern) for pattern in patterns):
                return category
        return None
    
    def _save_page_view_async(self, user, url_path, url_name=None, view_name=None, 
                              page_category=None, ip_address=None, user_agent=None):
        """Salva a visualização de forma assíncrona"""
        try:
            # Importa aqui para evitar import circular
            from apps.main.home.models import PageView
            
            # Usa transaction.on_commit para salvar após a resposta ser enviada
            def save_view():
                try:
                    PageView.objects.create(
                        user=user,
                        url_path=url_path,
                        url_name=url_name,
                        view_name=view_name,
                        page_category=page_category,
                        ip_address=ip_address,
                        user_agent=user_agent
                    )
                except Exception as e:
                    logger.error(f"Erro ao salvar PageView: {e}", exc_info=True)
            
            # Salva após o commit da transação atual
            transaction.on_commit(save_view)
            
        except Exception as e:
            logger.error(f"Erro ao preparar salvamento de PageView: {e}", exc_info=True)

