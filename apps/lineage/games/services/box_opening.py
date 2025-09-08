import random
from apps.lineage.games.models import *

def open_box(user, box_id):
    try:
        box = Box.objects.get(id=box_id)
    except Box.DoesNotExist:
        return None, "Caixa não encontrada."

    # Pega apenas boosters que ainda não foram usados
    items = list(box.items.filter(opened=False))
    if not items:
        return None, "Sem boosters disponíveis na caixa."

    # Sorteia um booster com base na probabilidade
    selected_item = random.choices(
        items,
        weights=[item.probability for item in items],
        k=1
    )[0]

    # Marca o booster como usado
    selected_item.opened = True
    selected_item.save()

    # Garante que o usuário tem uma bag
    bag, created = Bag.objects.get_or_create(user=user)

    # Adiciona o item à bag
    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=selected_item.item.item_id,
        enchant=selected_item.item.enchant,
        defaults={
            'item_name': selected_item.item.name,
            'quantity': 1,
        }
    )

    if not created:
        bag_item.quantity += 1
        bag_item.save()

    # Registro no histórico
    BoxItemHistory.objects.create(
        user=user,
        item=selected_item.item,
        box=box,
        rarity=selected_item.item.rarity,
        enchant=selected_item.item.enchant
    )

    return selected_item.item, None
