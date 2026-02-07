from django import template
from datetime import timedelta

register = template.Library()


@register.simple_tag
def get_custom_tops():
    """Retorna tops customizados ativos para o menu."""
    try:
        from apps.lineage.server.models import CustomTop
        return list(CustomTop.objects.filter(active=True).order_by('order', 'title'))
    except Exception:
        return []

@register.filter
def get_dict_item(obj, key):
    """Retorna obj[key] para dicts."""
    if hasattr(obj, 'get'):
        return obj.get(key, '')
    return getattr(obj, str(key), '')


@register.filter
def humanize_time(seconds):
    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")

    return ' '.join(parts) if parts else "0m"
