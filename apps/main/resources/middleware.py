from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


class ResourceAccessMiddleware:
    """
    Middleware para verificar se os recursos estão ativos antes de permitir acesso
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Mapeamento de caminhos de URL para recursos
        self.path_mapping = {
            # Shop
            '/app/shop/': 'shop_module',
            '/app/shop/cart/': 'shop_cart',
            '/app/shop/cart/add-item/': 'shop_cart',
            '/app/shop/cart/add-package/': 'shop_cart',
            '/app/shop/cart/checkout/': 'shop_checkout',
            '/app/shop/purchases/': 'shop_purchases',
            '/app/shop/manager/dashboard/': 'shop_dashboard',
            
            # Wallet
            '/app/wallet/': 'wallet_module',
            '/app/wallet/dashboard/': 'wallet_dashboard',
            '/app/wallet/transfer/': 'wallet_transfer',
            '/app/wallet/history/': 'wallet_history',
            
            # Social
            '/social/': 'social_module',
            '/social/feed/': 'social_feed',
            '/social/profile/': 'social_profile',
            '/social/search/': 'social_search',
            
            # Games
            '/app/game/': 'games_module',
            '/app/game/battle-pass/': 'battle_pass',
            '/app/game/box-opening/': 'box_opening',
            '/app/game/roulette/': 'roulette',
            
            # Auction
            '/app/auction/': 'auction_module',
            '/app/auction/list/': 'auction_list',
            '/app/auction/create/': 'auction_create',
            
            # Inventory
            '/app/inventory/': 'inventory_module',
            '/app/inventory/dashboard/': 'inventory_dashboard',
            
            # Payment
            '/app/payment/': 'payment_module',
            '/app/payment/process/': 'payment_process',
            '/app/payment/history/': 'payment_history',
        }

    def __call__(self, request):
        # Log para debug
        logger.info(f"Middleware executando para caminho: {request.path}")
        
        # Verifica se o recurso está ativo
        if not self._check_resource_access(request):
            logger.warning(f"Recurso inativo detectado para caminho: {request.path}")
            return self._handle_inactive_resource(request)
        
        response = self.get_response(request)
        return response

    def _check_resource_access(self, request):
        """
        Verifica se o usuário pode acessar o recurso solicitado
        """
        try:
            from .models import SystemResource
            
            # Pega o caminho da requisição
            path = request.path
            
            # Verifica se o caminho está mapeado para algum recurso
            resource_name = None
            
            # Primeiro, verifica mapeamento exato por caminho
            if path in self.path_mapping:
                resource_name = self.path_mapping[path]
            else:
                # Verifica mapeamento por prefixo (para URLs com parâmetros)
                for mapped_path, mapped_resource in self.path_mapping.items():
                    if path.startswith(mapped_path):
                        resource_name = mapped_resource
                        break
            
            # Se encontrou um recurso, verifica se está ativo
            if resource_name:
                # Verifica hierarquia de recursos
                is_active = self._check_resource_hierarchy(resource_name)
                logger.info(f"Verificando recurso '{resource_name}' para caminho '{path}': {'ATIVO' if is_active else 'INATIVO'}")
                return is_active
            
            return True  # Se não há recurso mapeado, permite acesso
            
        except Exception as e:
            logger.error(f"Erro ao verificar acesso ao recurso: {e}")
            return True  # Em caso de erro, permite acesso por segurança

    def _check_resource_hierarchy(self, resource_name):
        """
        Verifica se um recurso está ativo considerando a hierarquia
        """
        from .models import SystemResource
        
        # Define a hierarquia de recursos
        hierarchy = {
            # Games - se games_module estiver inativo, todos os jogos ficam inativos
            'battle_pass': 'games_module',
            'box_opening': 'games_module', 
            'roulette': 'games_module',
            
            # Shop - se shop_module estiver inativo, todos os recursos da shop ficam inativos
            'shop_dashboard': 'shop_module',
            'shop_items': 'shop_module',
            'shop_packages': 'shop_module',
            'shop_cart': 'shop_module',
            'shop_checkout': 'shop_module',
            'shop_purchases': 'shop_module',
            
            # Wallet - se wallet_module estiver inativo, todos os recursos da wallet ficam inativos
            'wallet_dashboard': 'wallet_module',
            'wallet_transfer': 'wallet_module',
            'wallet_history': 'wallet_module',
            
            # Social - se social_module estiver inativo, todos os recursos sociais ficam inativos
            'social_feed': 'social_module',
            'social_profile': 'social_module',
            'social_search': 'social_module',
            
            # Auction - se auction_module estiver inativo, todos os recursos de leilão ficam inativos
            'auction_list': 'auction_module',
            'auction_create': 'auction_module',
            
            # Inventory - se inventory_module estiver inativo, todos os recursos de inventário ficam inativos
            'inventory_dashboard': 'inventory_module',
            
            # Payment - se payment_module estiver inativo, todos os recursos de pagamento ficam inativos
            'payment_process': 'payment_module',
            'payment_history': 'payment_module',
        }
        
        # Verifica se o recurso tem um módulo pai
        if resource_name in hierarchy:
            parent_module = hierarchy[resource_name]
            
            # Primeiro verifica se o módulo pai está ativo
            parent_active = SystemResource.is_resource_active(parent_module)
            if not parent_active:
                logger.info(f"Módulo pai '{parent_module}' está inativo, bloqueando '{resource_name}'")
                return False
            
            # Se o módulo pai está ativo, verifica o recurso específico
            resource_active = SystemResource.is_resource_active(resource_name)
            return resource_active
        else:
            # Se não tem módulo pai, verifica apenas o recurso
            return SystemResource.is_resource_active(resource_name)

    def _handle_inactive_resource(self, request):
        """
        Lida com tentativas de acesso a recursos inativos
        """
        from django.shortcuts import render
        from django.http import HttpResponseNotFound
        
        # Para todos os usuários, bloqueia o acesso
        if request.user.is_staff:
            # Staff vê página 404 personalizada com informações técnicas
            try:
                return render(request, 'resources/404.html', status=404)
            except Exception as e:
                logger.error(f"Erro ao renderizar template 404 para staff: {e}")
                # Fallback para HTML simples para staff
                return HttpResponseNotFound(
                    '<!DOCTYPE html>'
                    '<html><head><title>Recurso Indisponível</title></head>'
                    '<body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">'
                    '<h1 style="color: #dc3545;">404 - Recurso Indisponível</h1>'
                    '<p>Este recurso está temporariamente indisponível.</p>'
                    '<p><strong>Info Técnica:</strong> Caminho: ' + request.path + '</p>'
                    '<p><a href="/pages/dashboard/">Voltar ao Dashboard</a></p>'
                    '</body></html>'
                )
        else:
            # Usuário comum vê a página 404 padrão do sistema
            try:
                return render(request, 'errors/404.html', status=404)
            except Exception as e:
                logger.error(f"Erro ao renderizar template 404 padrão: {e}")
                # Fallback para HTML simples para usuário comum
                return HttpResponseNotFound(
                    '<!DOCTYPE html>'
                    '<html><head><title>Página não encontrada</title></head>'
                    '<body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">'
                    '<h1 style="color: #dc3545;">404 - Página não encontrada</h1>'
                    '<p>A página que você está procurando não existe ou foi movida.</p>'
                    '<p><a href="/pages/dashboard/">Voltar ao Dashboard</a></p>'
                    '</body></html>'
                )
