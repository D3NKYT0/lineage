from django import template
from django.conf import settings
import random
from apps.lineage.server.models import ApoiadorDefault

register = template.Library()

@register.simple_tag
def apoiador_image_url(apoiador):
    if apoiador.imagem:
        return apoiador.imagem.url
    else:
        # Escolhe uma imagem padrão aleatória entre 1 e 5
        random_number = random.randint(1, 5)
        return f"{settings.STATIC_URL}assets/img/apoiadores/apoio{random_number}.png"

@register.simple_tag
def imagens_default_apoiadores():
    imagens = [img.imagem.url for img in ApoiadorDefault.objects.all()]
    if imagens:
        return imagens
    # fallback para imagens padrão do static
    static_url = settings.STATIC_URL + 'assets/img/apoiadores/'
    return [f"{static_url}apoio{i}.png" for i in range(1, 6)] 