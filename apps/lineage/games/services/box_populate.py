import random
from apps.lineage.games.models import *


def populate_box_with_items(box):
    box_type = box.box_type
    all_items = box_type.allowed_items.filter(can_be_populated=True)

    rarities = {
        'common': box_type.chance_common,
        'rare': box_type.chance_rare,
        'epic': box_type.chance_epic,
        'legendary': box_type.chance_legendary,
    }

    total_chance = sum(rarities.values())
    if total_chance != 100:
        raise ValueError(f"A soma das chances não é 100%. Soma atual: {total_chance}")

    boosters_count = box_type.boosters_amount
    boosters_by_rarity = {
        rarity: int((boosters_count * chance) / 100)
        for rarity, chance in rarities.items()
    }

    # Corrigir diferenças causadas por arredondamento
    difference = boosters_count - sum(boosters_by_rarity.values())
    for rarity in sorted(rarities, key=lambda x: rarities[x], reverse=True):
        if difference > 0:
            boosters_by_rarity[rarity] += 1
            difference -= 1

    # Aplicar limites (se configurados) para épico e lendário
    if box_type.max_epic_items > 0:
        boosters_by_rarity['epic'] = min(boosters_by_rarity['epic'], box_type.max_epic_items)

    if box_type.max_legendary_items > 0:
        boosters_by_rarity['legendary'] = min(boosters_by_rarity['legendary'], box_type.max_legendary_items)

    # Populando os itens
    for rarity, count in boosters_by_rarity.items():
        if count > 0:
            candidates = all_items.filter(rarity=rarity)
            if not candidates.exists():
                continue

            for _ in range(count):
                selected_item = random.choice(list(candidates))
                BoxItem.objects.create(
                    box=box,
                    item=selected_item,
                    probability=1.0
                )
