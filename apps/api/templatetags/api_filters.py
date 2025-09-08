from django import template

register = template.Library()

@register.filter
def format_endpoint_name(value):
    """Formata o nome do endpoint para exibição"""
    return value.replace('_', ' ').title()

@register.filter
def format_endpoint_url(value):
    """Formata o nome do endpoint para URL"""
    return value.replace('_', '-')

@register.filter
def remove_prefix(value, prefix):
    """Remove um prefixo de uma string"""
    if value.startswith(prefix):
        return value[len(prefix):]
    return value

@register.filter
def auth_endpoint_url(value):
    """Formata URL para endpoints de autenticação"""
    if value.startswith('auth_'):
        return value[5:].replace('_', '-')
    return value.replace('_', '-')

@register.filter
def user_endpoint_url(value):
    """Formata URL para endpoints de usuário"""
    if value.startswith('user_'):
        return value[5:].replace('_', '-')
    return value.replace('_', '-')

@register.filter
def search_endpoint_url(value):
    """Formata URL para endpoints de busca"""
    if value.startswith('search_'):
        return value[7:].replace('_', '-')
    return value.replace('_', '-')

@register.filter
def admin_endpoint_url(value):
    """Formata URL para endpoints de administração"""
    if value.startswith('api_'):
        return value[4:].replace('_', '-')
    return value.replace('_', '-') 