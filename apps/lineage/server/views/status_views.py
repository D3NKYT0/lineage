from django.shortcuts import render
from apps.main.home.decorator import conditional_otp_required
from django.utils.translation import gettext as _

import json, os, time
from django.conf import settings

from datetime import datetime, timedelta
from apps.lineage.server.database import LineageDB
from apps.lineage.server.utils.crest import attach_crests_to_clans
from utils.resources import get_class_name

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


@conditional_otp_required
def siege_ranking_view(request):
    db = LineageDB()
    if db.is_connected():
        castles = LineageStats.siege()

        for castle in castles:
            participants = LineageStats.siege_participants(castle["id"])
            castle["attackers"] = [p for p in participants if p["type"] == "0"]
            castle["defenders"] = [p for p in participants if p["type"] == "1"]

            # adiciona caminho da imagem baseado no nome
            castle["image_path"] = f"assets/img/castles/{castle['name'].lower()}.jpg"

            # adiciona valores default traduzidos se vazio
            castle["clan_name"] = castle["clan_name"] or _("No Owner")
            castle["char_name"] = castle["char_name"] or _("No Leader")
            castle["ally_name"] = castle["ally_name"] or _("No Alliance")

            # CORREÇÃO AQUI: converte Decimal para float
            timestamp_s = float(castle["sdate"]) / 1000
            castle["sdate"] = datetime.fromtimestamp(timestamp_s)

        # move para fora do loop para não sobrescrever a cada iteração
        castles = attach_crests_to_clans(castles)

    else:
        castles = list()

    return render(request, "status/siege_ranking.html", {"castles": castles})


@conditional_otp_required
def olympiad_ranking_view(request):
    # Obtém o ranking de olimpíada
    db = LineageDB()
    original_result = LineageStats.olympiad_ranking() if db.is_connected() else []
    
    # Filtra registros com valores None
    filtered_result = []
    for player in original_result:
        # Só inclui se char_name não for None
        if player.get('char_name') is not None:
            filtered_result.append(player)
    
    # Preparar dados para os filtros - usar dados originais ANTES de qualquer filtro
    # Usar a mesma lógica da view que funciona
    all_classes = list(set([get_class_name(p.get('base', '')) for p in filtered_result if p.get('base')]))
    all_classes.sort()
    
    # Aplicar filtros baseados nos parâmetros GET
    search_query = request.GET.get('search', '').strip().lower()
    class_filter = request.GET.get('class', '').strip()
    clan_filter = request.GET.get('clan', '').strip().lower()
    status_filter = request.GET.get('status', '').strip()
    min_points = request.GET.get('min_points', '').strip()
    
    # Filtrar por busca de texto (nome do jogador, clã, classe)
    if search_query:
        filtered_result = [
            player for player in filtered_result
            if ((player.get('char_name') or '').lower().find(search_query) != -1 or
                (player.get('clan_name') or '').lower().find(search_query) != -1 or
                get_class_name(player.get('base', '')).lower().find(search_query) != -1)
        ]
    
    # Filtrar por classe
    if class_filter:
        filtered_result = [
            player for player in filtered_result
            if get_class_name(player.get('base', '')).lower() == class_filter.lower()
        ]
    
    # Filtrar por clã
    if clan_filter:
        filtered_result = [
            player for player in filtered_result
            if (player.get('clan_name') or '').lower().find(clan_filter) != -1
        ]
    
    # Filtrar por status
    if status_filter:
        if status_filter == 'online':
            filtered_result = [player for player in filtered_result if player.get('online', 0) > 0]
        elif status_filter == 'offline':
            filtered_result = [player for player in filtered_result if player.get('online', 0) == 0]
    
    # Filtrar por pontos mínimos
    if min_points and min_points.isdigit():
        min_points_int = int(min_points)
        filtered_result = [
            player for player in filtered_result
            if player.get('olympiad_points', 0) >= min_points_int
        ]
    
    # Processar os dados para incluir nome da classe (como na view que funciona)
    for player in filtered_result:
        if 'base' in player and player['base'] is not None:
            player['class_name'] = get_class_name(player['base'])
        else:
            player['class_name'] = '-'
    
    final_result = attach_crests_to_clans(filtered_result)
    
    context = {
        'ranking': final_result,
        'filters': {
            'search': request.GET.get('search', ''),
            'class': request.GET.get('class', ''),
            'clan': request.GET.get('clan', ''),
            'status': request.GET.get('status', ''),
            'min_points': request.GET.get('min_points', ''),
        },
        'available_classes': all_classes,
        'total_players': len(original_result),
        'filtered_players': len(filtered_result),
    }
    
    return render(request, 'status/olympiad_ranking.html', context)


@conditional_otp_required
def olympiad_all_heroes_view(request):
    # Obtém todos os heróis da olimpíada
    db = LineageDB()
    result = LineageStats.olympiad_all_heroes() if db.is_connected() else []
    
    # Filtra registros com valores None
    filtered_result = []
    for player in result:
        # Só inclui se char_name não for None
        if player.get('char_name') is not None:
            filtered_result.append(player)
    
    result = attach_crests_to_clans(filtered_result)
    for player in result:
        player['base'] = get_class_name(player['base'])
    return render(request, 'status/olympiad_all_heroes.html', {'heroes': result})


@conditional_otp_required
def olympiad_current_heroes_view(request):
    # Obtém os heróis atuais da olimpíada
    db = LineageDB()
    result = LineageStats.olympiad_current_heroes() if db.is_connected() else []
    
    # Filtra registros com valores None
    filtered_result = []
    for player in result:
        # Só inclui se char_name não for None
        if player.get('char_name') is not None:
            filtered_result.append(player)
    
    result = attach_crests_to_clans(filtered_result)
    for player in result:
        player['base'] = get_class_name(player['base'])
    return render(request, 'status/olympiad_current_heroes.html', {'current_heroes': result})


@conditional_otp_required
def boss_jewel_locations_view(request):

    db = LineageDB()
    if db.is_connected():

        boss_jewel_ids = [6656, 6657, 6658, 6659, 6660, 6661, 8191]
        jewel_locations = LineageStats.boss_jewel_locations(boss_jewel_ids)

        # Caminho para o itens.json
        itens_path = os.path.join(settings.BASE_DIR, 'utils/data/itens.json')
        with open(itens_path, 'r', encoding='utf-8') as f:
            itens_data = json.load(f)

        # Substituir item_id pelo item_name
        for loc in jewel_locations:
            item_id_str = str(loc['item_id'])
            item_name = itens_data.get(item_id_str, ["Desconhecido"])[0]
            loc['item_name'] = item_name

        # adiciona as crests dos clans
        jewel_locations = attach_crests_to_clans(jewel_locations)    

    else:
        jewel_locations = list()

    return render(request, 'status/boss_jewel_locations.html', {'jewel_locations': jewel_locations})


@conditional_otp_required
def grandboss_status_view(request):

    db = LineageDB()
    if db.is_connected():

        grandboss_status = LineageStats.grandboss_status()

        # Carregar o JSON de bosses
        bosses_path = os.path.join(settings.BASE_DIR, 'utils/data/bosses.json')
        with open(bosses_path, 'r', encoding='utf-8') as f:
            bosses_data = json.load(f)

        bosses_index = {str(boss['id']): boss for boss in bosses_data['data']}

        # Enriquecer os dados
        for boss in grandboss_status:
            boss_id_str = str(boss['boss_id'])
            boss_info = bosses_index.get(boss_id_str, {"name": "Desconhecido", "level": "-"})

            boss['name'] = boss_info['name']
            boss['level'] = boss_info['level']

            respawn_timestamp = boss.get('respawn')
            gmt_offset = int(getattr(settings, 'GMT_OFFSET', 0))
            current_time = time.time()

            # Validar tipo e converter se necessário
            if isinstance(respawn_timestamp, (int, float)):
                if respawn_timestamp > 1e12:
                    # Está em milissegundos, converte para segundos
                    respawn_timestamp /= 1000

                if respawn_timestamp > current_time:
                    try:
                        respawn_datetime = datetime.fromtimestamp(respawn_timestamp) - timedelta(hours=gmt_offset)
                        
                        # Usar configuração para decidir se mostra data e hora ou apenas data
                        if getattr(settings, 'GRANDBOSS_SHOW_TIME', True):
                            boss['respawn_human'] = respawn_datetime.strftime('%d/%m/%Y %H:%M')
                        else:
                            boss['respawn_human'] = respawn_datetime.strftime('%d/%m/%Y')
                        
                        boss['status'] = "Morto"
                    except (OSError, OverflowError, ValueError) as e:
                        boss['status'] = "Desconhecido"
                        boss['respawn_human'] = f"Erro: {str(e)}"
                else:
                    boss['status'] = "Vivo"
                    boss['respawn_human'] = '-'
            else:
                boss['status'] = "Desconhecido"
                boss['respawn_human'] = 'Timestamp inválido'

    else:
        grandboss_status = list()

    return render(request, 'status/grandboss_status.html', {'bosses': grandboss_status})
