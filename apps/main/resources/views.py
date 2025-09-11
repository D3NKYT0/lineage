from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json

from .models import SystemResource


def _get_parent_module(resource_name):
    """Retorna o módulo pai de um recurso"""
    hierarchy = {
        'battle_pass': 'games_module',
        'box_opening': 'games_module', 
        'roulette': 'games_module',
        'shop_dashboard': 'shop_module',
        'shop_items': 'shop_module',
        'shop_packages': 'shop_module',
        'shop_cart': 'shop_module',
        'shop_checkout': 'shop_module',
        'shop_purchases': 'shop_module',
        'wallet_dashboard': 'wallet_module',
        'wallet_transfer': 'wallet_module',
        'wallet_history': 'wallet_module',
        'social_feed': 'social_module',
        'social_profile': 'social_module',
        'social_search': 'social_module',
        'auction_list': 'auction_module',
        'auction_create': 'auction_module',
        'inventory_dashboard': 'inventory_module',
        'payment_process': 'payment_module',
        'payment_history': 'payment_module',
    }
    return hierarchy.get(resource_name)


def _is_parent_active(resource_name):
    """Verifica se o módulo pai está ativo"""
    parent_module = _get_parent_module(resource_name)
    if parent_module:
        try:
            parent_resource = SystemResource.objects.get(name=parent_module)
            return parent_resource.is_active
        except SystemResource.DoesNotExist:
            return True
    return True


def _is_effectively_active(resource_name):
    """Verifica se o recurso está efetivamente ativo (considerando hierarquia)"""
    try:
        resource = SystemResource.objects.get(name=resource_name)
        if not resource.is_active:
            return False
        
        # Se tem módulo pai, verifica se está ativo
        parent_module = _get_parent_module(resource_name)
        if parent_module:
            return _is_parent_active(resource_name)
        
        return True
    except SystemResource.DoesNotExist:
        return False


def is_staff_user(user):
    """Verifica se o usuário é staff"""
    return user.is_staff


@login_required
@user_passes_test(is_staff_user)
def resources_dashboard(request):
    """
    Dashboard principal dos recursos do sistema
    """
    # Define a hierarquia de recursos (módulos master)
    master_modules = {
        'shop_module', 'wallet_module', 'social_module', 'games_module',
        'auction_module', 'inventory_module', 'payment_module', 
        'notification_module', 'admin_module', 'api_module'
    }
    
    # Pega apenas os módulos master para estatísticas
    master_resources = SystemResource.objects.filter(name__in=master_modules)
    total_master_resources = master_resources.count()
    active_master_resources = master_resources.filter(is_active=True).count()
    inactive_master_resources = total_master_resources - active_master_resources
    
    # Calcula percentual baseado apenas nos módulos master
    master_percentage = (active_master_resources / total_master_resources * 100) if total_master_resources > 0 else 0
    
    # Pega todos os recursos organizados por categoria
    resources_by_category = SystemResource.get_all_resources_by_category()
    
    # Adiciona informações de hierarquia para cada recurso
    for category, resources in resources_by_category.items():
        for resource in resources:
            resource.is_master = resource.name in master_modules
            resource.parent_module = _get_parent_module(resource.name)
            resource.is_parent_active = _is_parent_active(resource.name)
            resource.is_effectively_active = _is_effectively_active(resource.name)
    
    context = {
        'resources_by_category': resources_by_category,
        'total_master_resources': total_master_resources,
        'active_master_resources': active_master_resources,
        'inactive_master_resources': inactive_master_resources,
        'master_percentage': round(master_percentage, 1),
        'page_title': _('Painel de Recursos do Sistema'),
    }
    
    return render(request, 'resources/dashboard.html', context)


@login_required
@user_passes_test(is_staff_user)
@require_http_methods(["POST"])
def toggle_resource(request, resource_name):
    """
    Alterna o status de um recurso específico via AJAX
    """
    try:
        resource = get_object_or_404(SystemResource, name=resource_name)
        resource.is_active = not resource.is_active
        resource.save()
        
        return JsonResponse({
            'success': True,
            'is_active': resource.is_active,
            'message': _('Recurso {} com sucesso.').format(
                _('ativado') if resource.is_active else _('desativado')
            )
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _('Erro ao alterar status do recurso: {}').format(str(e))
        })


@login_required
@user_passes_test(is_staff_user)
def resources_by_category(request, category):
    """
    Exibe recursos de uma categoria específica
    """
    resources = SystemResource.objects.filter(category=category).order_by('order', 'display_name')
    
    if not resources.exists():
        messages.warning(request, _('Nenhum recurso encontrado para a categoria "{}".').format(category))
        return redirect('resources:dashboard')
    
    # Estatísticas da categoria
    total_resources = resources.count()
    active_resources = resources.filter(is_active=True).count()
    
    context = {
        'resources': resources,
        'category': category,
        'total_resources': total_resources,
        'active_resources': active_resources,
        'page_title': _('Recursos - {}').format(category.title()),
    }
    
    return render(request, 'resources/category.html', context)
