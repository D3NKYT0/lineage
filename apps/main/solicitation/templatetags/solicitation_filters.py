from django import template

register = template.Library()

@register.filter
def in_list(value, arg):
    """
    Verifica se um valor está em uma lista de strings separadas por vírgula
    Uso: {{ solicitation.status|in_list:"resolved,closed,cancelled,rejected" }}
    """
    if not value or not arg:
        return False
    
    # Converte a string de argumentos em uma lista
    arg_list = [item.strip() for item in arg.split(',')]
    
    # Verifica se o valor está na lista
    return value in arg_list