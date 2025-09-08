# apps/lineage/inventory/templatetags/itens_extras.py
import os
from django import template
from django.conf import settings
from django.core.files.storage import default_storage
from apps.lineage.inventory.models import CustomItem


register = template.Library()


@register.simple_tag
def item_image_url(item_id):
    try:
        custom_item = CustomItem.objects.get(item_id=item_id)
        return custom_item.imagem.url if custom_item.imagem else f"{settings.STATIC_URL}assets/img/l2/icons/default.jpg"
    except CustomItem.DoesNotExist:
        item_image_path = os.path.join(settings.BASE_DIR, 'static/assets/img/l2/icons/5-{}.jpg'.format(item_id))
        if os.path.exists(item_image_path):
            return f"{settings.STATIC_URL}assets/img/l2/icons/5-{item_id}.jpg"
        else:
            return f"{settings.STATIC_URL}assets/img/l2/icons/default.jpg"
