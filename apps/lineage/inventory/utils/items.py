import os
import json
from django.conf import settings
from apps.lineage.inventory.models import CustomItem

def get_itens_json():
    # Caminho para o itens.json
    itens_path = os.path.join(settings.BASE_DIR, 'utils/data/itens.json')
    
    # Carrega itens.json
    with open(itens_path, 'r', encoding='utf-8') as f:
        itens_data = json.load(f)

    # Carrega itens customizados do banco
    custom_items = CustomItem.objects.all()

    # Adiciona os itens customizados no JSON
    for item in custom_items:
        itens_data[str(item.item_id)] = [item.nome]

    return itens_data
