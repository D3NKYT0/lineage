from django import template
from django.utils.translation import gettext_lazy as _
from ..models import SystemResource

register = template.Library()


@register.simple_tag
def is_resource_active(resource_name):
    """
    Verifica se um recurso específico está ativo
    """
    return SystemResource.is_resource_active(resource_name)


@register.inclusion_tag('resources/resource_status_badge.html')
def resource_status_badge(resource_name, show_text=True):
    """
    Exibe um badge de status para um recurso
    """
    is_active = SystemResource.is_resource_active(resource_name)
    return {
        'is_active': is_active,
        'show_text': show_text,
    }


@register.simple_tag
def get_active_resources_by_category(category):
    """
    Retorna todos os recursos ativos de uma categoria específica
    """
    return SystemResource.get_active_resources_by_category(category)


@register.simple_tag
def get_all_resources_by_category():
    """
    Retorna todos os recursos organizados por categoria
    """
    return SystemResource.get_all_resources_by_category()


@register.filter
def resource_is_active(resource_name):
    """
    Filtro para verificar se um recurso está ativo
    """
    return SystemResource.is_resource_active(resource_name)
