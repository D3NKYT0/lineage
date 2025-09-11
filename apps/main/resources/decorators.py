from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import Http404
from .models import SystemResource


def require_resource(resource_name, redirect_url=None, show_message=True):
    """
    Decorator para verificar se um recurso está ativo antes de permitir acesso à view
    
    Args:
        resource_name (str): Nome do recurso a ser verificado
        redirect_url (str): URL para redirecionar se o recurso estiver inativo
        show_message (bool): Se deve mostrar mensagem de erro
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Staff sempre pode acessar
            if request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            # Verifica se o recurso está ativo
            if not SystemResource.is_resource_active(resource_name):
                if show_message:
                    messages.warning(
                        request, 
                        _('Este recurso está temporariamente indisponível. Tente novamente mais tarde.')
                    )
                
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    # Redireciona para o dashboard por padrão
                    return redirect('dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def require_shop_module(view_func):
    """
    Decorator específico para o módulo da loja
    """
    return require_resource('shop_module')(view_func)


def require_wallet_module(view_func):
    """
    Decorator específico para o módulo da carteira
    """
    return require_resource('wallet_module')(view_func)


def require_social_module(view_func):
    """
    Decorator específico para o módulo da rede social
    """
    return require_resource('social_module')(view_func)


def require_games_module(view_func):
    """
    Decorator específico para o módulo de jogos
    """
    return require_resource('games_module')(view_func)


def require_auction_module(view_func):
    """
    Decorator específico para o módulo de leilões
    """
    return require_resource('auction_module')(view_func)


def require_inventory_module(view_func):
    """
    Decorator específico para o módulo do inventário
    """
    return require_resource('inventory_module')(view_func)


def require_payment_module(view_func):
    """
    Decorator específico para o módulo de pagamentos
    """
    return require_resource('payment_module')(view_func)
