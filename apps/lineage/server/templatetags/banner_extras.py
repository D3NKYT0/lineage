from django import template
from django.template.defaultfilters import stringfilter
from ..models import IndexConfig

register = template.Library()


@register.simple_tag
def get_banner_image():
    """
    Retorna a imagem do banner configurada no admin
    """
    try:
        config = IndexConfig.objects.first()
        if config and config.imagem_banner:
            return config.imagem_banner
    except:
        pass
    return None


@register.simple_tag
def get_banner_url():
    """
    Retorna a URL da imagem do banner configurada no admin
    """
    try:
        config = IndexConfig.objects.first()
        if config and config.imagem_banner:
            return config.imagem_banner.url
    except:
        pass
    return None 