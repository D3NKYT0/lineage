from django import template
import json
from apps.lineage.games.models import BoxItem
from apps.lineage.games.choices import RARITY_CHOICES


register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_item_list_json(box_type):
    box_items = BoxItem.objects.filter(box__box_type=box_type).select_related('item')
    if not box_items.exists():
        return json.dumps([])

    unique_items = {bi.item for bi in box_items}

    return json.dumps([
        {
            'name': item.name,
            'rarity': item.rarity,
            'rarity_display': dict(RARITY_CHOICES).get(item.rarity, item.rarity),
            'enchant': item.enchant,
            'image_url': item.image.url if item.image else None
        } for item in unique_items
    ])


