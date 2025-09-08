from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.utils.translation import gettext as _
from django.urls import reverse
from apps.main.social.models import ContentFilter, Report, ModerationLog
from django.contrib.auth import get_user_model

User = get_user_model()


class ContentFilterMiddleware(MiddlewareMixin):
    """
    Middleware para bloqueios críticos de conteúdo (auto_delete)
    Outros filtros são processados pelos signals após criação
    """
    
    def process_request(self, request):
        """Processa a requisição antes da view"""
        # Apenas para requisições POST que criam conteúdo
        if request.method == 'POST':
            # Verificar se é criação de post ou comentário
            if any(path in request.path for path in ['/social/feed/', '/social/post/create/', '/social/post/']):
                # Verificar filtros de bloqueio crítico
                return self._check_critical_filters(request)
        return None
    
    def _check_critical_filters(self, request):
        """Verifica apenas filtros críticos que bloqueiam criação (auto_delete)"""
        try:
            # Obter apenas filtros de bloqueio crítico
            critical_filters = ContentFilter.objects.filter(
                is_active=True, 
                action='auto_delete'
            )
            
            if not critical_filters.exists():
                return None
            
            # Verificar se há dados POST
            if not request.POST:
                return None
            
            # Extrair conteúdo para verificação
            content = request.POST.get('content') or request.POST.get('comment_content')
            if not content:
                return None
            
            # Verificar filtros críticos
            for content_filter in critical_filters:
                if content_filter.matches_content(content):
                    # Adicionar mensagem de erro usando Django messages
                    error_message = _('Conteúdo bloqueado por violar nossas diretrizes')
                    if content_filter.name:
                        error_message += f' (Filtro: {content_filter.name})'
                    messages.error(request, error_message)
                    
                    # Verificar se é uma requisição AJAX
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        # Para AJAX, ainda retornar JSON mas com redirecionamento
                        return JsonResponse({
                            'error': error_message,
                            'redirect': reverse('social:feed')
                        }, status=400)
                    
                    # Para requisições normais, redirecionar
                    referer = request.META.get('HTTP_REFERER')
                    if referer:
                        return HttpResponseRedirect(referer)
                    else:
                        # Se não houver referer, redirecionar para o feed
                        return HttpResponseRedirect(reverse('social:feed'))
                
        except Exception as e:
            print(f"Erro ao verificar filtros críticos: {e}")
        
        return None


class SpamProtectionMiddleware(MiddlewareMixin):
    """
    Middleware para proteção contra spam
    """
    
    def process_request(self, request):
        """Verifica sinais de spam na requisição"""
        # Verificar se o spam protection está desabilitado via variável de ambiente
        import os
        if os.environ.get('DISABLE_SPAM_PROTECTION', 'False').lower() == 'true':
            return None
            
        if request.method == 'POST':
            # Verificar se é criação de conteúdo
            if any(path in request.path for path in ['/social/feed/', '/social/post/create/']):
                is_spam = self._is_spam_request(request)
                if is_spam:
                    # Log para debugging
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Spam detectado para usuário {request.user.username if request.user.is_authenticated else 'anonymous'}")
                    logger.warning(f"Conteúdo: {request.POST.get('content', '')[:100]}...")
                    
                    return JsonResponse({
                        'error': _('Atividade suspeita detectada. Tente novamente em alguns minutos.')
                    }, status=429)
        return None
    
    def _is_spam_request(self, request):
        """Verifica se a requisição parece ser spam"""
        # Verificar frequência de posts (implementar cache/rate limiting)
        if request.user.is_authenticated:
            # Verificar se o usuário fez muitos posts recentemente
            from django.utils import timezone
            from datetime import timedelta
            from apps.main.social.models import Post
            
            recent_posts = Post.objects.filter(
                author=request.user,
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).count()
            
            if recent_posts > 10:  # Mais de 10 posts em 5 minutos (mais permissivo)
                return True
            
            # Se o usuário tem posts anteriores e é um usuário estabelecido, ser mais permissivo
            total_posts = Post.objects.filter(author=request.user).count()
            if total_posts > 5:  # Usuários com mais de 5 posts são considerados estabelecidos
                # Para usuários estabelecidos, ser mais permissivo com URLs
                pass
        
        # Verificar conteúdo suspeito
        if request.POST:
            content = request.POST.get('content', '')
            
            # Padrões de spam mais específicos
            spam_patterns = [
                r'\b(buy|sell|cheap|discount|free|money|earn|rich)\b',
                r'\b(viagra|cialis|casino|poker|lottery)\b',
                r'\b(click here|visit now|limited time|act now)\b',
                # Padrões de spam com URLs específicos (versão mais robusta)
                r'http[s]?://[^\s<>"{}|\\^`\[\]]{1,2000}.*\b(buy|sell|cheap|discount|free|money|earn|rich|viagra|cialis|casino|poker|lottery)\b',
                r'http[s]?://[^\s<>"{}|\\^`\[\]]{1,2000}.*\b(click here|visit now|limited time|act now)\b',
            ]
            
            import re
            for pattern in spam_patterns:
                try:
                    if re.search(pattern, content, re.IGNORECASE):
                        return True
                except Exception:
                    # Em caso de erro na regex, continuar para o próximo padrão
                    continue
            
            # Verificar se há muitas URLs (mais de 5 URLs no mesmo post pode ser spam)
            try:
                url_count = len(re.findall(r'http[s]?://[^\s<>"{}|\\^`\[\]]{1,2000}', content))
                if url_count > 5:  # Aumentado de 3 para 5 URLs
                    return True
            except Exception:
                # Em caso de erro na regex, não bloquear
                pass
        
        return False
