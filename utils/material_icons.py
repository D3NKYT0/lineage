import json


def load_icons_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    icons = []
    for category in data.get('categories', []):
        for icon in category.get('icons', []):
            ligature = icon.get('ligature')
            if ligature:
                icons.append((ligature, ligature))
    return icons


# Carregue os ícones do JSON
MATERIAL_SYMBOLS = load_icons_from_json('utils/data/material_symbols.json')
