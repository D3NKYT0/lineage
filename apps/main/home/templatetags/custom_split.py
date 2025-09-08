# apps/main/templatetags/custom_filters.py
from django import template
import random

register = template.Library()


@register.filter
def split(value, arg):
    """Divide uma string no delimitador 'arg'."""
    return value.split(arg)


@register.filter
def random_item(value):
    """Retorna item aleatório de uma lista."""
    if isinstance(value, list) and value:
        return random.choice(value)
    return ''

@register.filter
def sub(value, arg):
    """Subtrai arg de value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def to_range(value):
    """Converte um número em um range iterável no template."""
    try:
        return range(int(value))
    except:
        return []
