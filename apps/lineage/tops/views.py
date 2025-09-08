from django.shortcuts import render
from django.views.generic import TemplateView
from django.utils.translation import gettext_lazy as _
from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.lineage.server.database import LineageDB
from apps.lineage.server.models import ActiveAdenaExchangeItem
from datetime import datetime

from utils.dynamic_import import get_query_class  # importa o helper
LineageStats = get_query_class("LineageStats")  # carrega a classe certa com base no .env


class TopsBaseView(TemplateView):
    """Base view for tops pages"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context
    
    def get_title(self):
        return _('Tops')


class TopsHomeView(TopsBaseView):
    template_name = 'tops/home.html'
    
    def get_title(self):
        return _('Tops')


class TopsPvpView(TopsBaseView):
    template_name = 'tops/pvp.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.top_pvp(limit=20) if db.is_connected() else []
        
        # Processar os dados para incluir nome da classe
        from utils.resources import get_class_name
        for player in result:
            if 'base' in player and player['base'] is not None:
                player['class_name'] = get_class_name(player['base'])
            else:
                player['class_name'] = '-'
        
        result = attach_crests_to_clans(result)
        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking PvP')


class TopsPkView(TopsBaseView):
    template_name = 'tops/pk.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.top_pk(limit=20) if db.is_connected() else []
        
        # Processar os dados para incluir nome da classe
        from utils.resources import get_class_name
        for player in result:
            if 'base' in player and player['base'] is not None:
                player['class_name'] = get_class_name(player['base'])
            else:
                player['class_name'] = '-'
        
        result = attach_crests_to_clans(result)
        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking PK')


class TopsAdenaView(TopsBaseView):
    template_name = 'tops/adena.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()

        adn_billion_item = 0
        value_item = 1000000000

        # Buscar o item ativo
        active_item = ActiveAdenaExchangeItem.objects.filter(active=True).order_by('-created_at').first()
        if active_item:
            adn_billion_item = active_item.item_type
            value_item = active_item.value_item

        def humanize_time(seconds):
            from datetime import timedelta
            try:
                seconds = int(seconds)
            except Exception:
                return "0m"
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

        if db.is_connected():
            result = LineageStats.top_adena(limit=20, adn_billion_item=adn_billion_item, value_item=value_item)
            
            # Padronizar campo adena
            for player in result:
                if 'adenas' in player and 'adena' not in player:
                    player['adena'] = player['adenas']
                # Adicionar campo tempo online humanizado
                player['human_onlinetime'] = humanize_time(player.get('onlinetime', 0))

            # Processar os dados para incluir nome da classe
            from utils.resources import get_class_name
            for player in result:
                base_id = player.get('base')
                if base_id is not None:
                    try:
                        base_id = int(base_id)
                    except Exception:
                        base_id = None
                if base_id is not None:
                    player['class_name'] = get_class_name(base_id)
                else:
                    player['class_name'] = '-'
            
            result = attach_crests_to_clans(result)
        else:
            result = list()

        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking Adena')


class TopsClansView(TopsBaseView):
    template_name = 'tops/clans.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        clanes = LineageStats.top_clans(limit=20) if db.is_connected() else []
        clanes = attach_crests_to_clans(clanes)
        context['clans'] = clanes
        return context
    
    def get_title(self):
        return _('Ranking Clans')


class TopsLevelView(TopsBaseView):
    template_name = 'tops/level.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        
        def humanize_time(seconds):
            from datetime import timedelta
            try:
                seconds = int(seconds)
            except Exception:
                return "0m"
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

        result = LineageStats.top_level(limit=20) if db.is_connected() else []
        
        # Processar os dados para incluir nome da classe e tempo online humanizado
        from utils.resources import get_class_name
        for player in result:
            # Processar classe
            if 'base' in player and player['base'] is not None:
                player['class_name'] = get_class_name(player['base'])
            else:
                player['class_name'] = '-'
            
            # Adicionar campo tempo online humanizado
            player['human_onlinetime'] = humanize_time(player.get('onlinetime', 0))
        
        result = attach_crests_to_clans(result)
        context['players'] = result
        return context
    
    def get_title(self):
        return _('Ranking Nível')


class TopsOnlineView(TopsBaseView):
    template_name = 'tops/online.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        
        def humanize_time(seconds):
            from datetime import timedelta
            try:
                seconds = int(seconds)
            except Exception:
                return "0m"
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

        result = LineageStats.top_online(limit=20) if db.is_connected() else []
        
        # Processar os dados para incluir nome da classe e tempo online humanizado
        from utils.resources import get_class_name
        for player in result:
            # Processar classe
            if 'base' in player and player['base'] is not None:
                player['class_name'] = get_class_name(player['base'])
            else:
                player['class_name'] = '-'
            
            # Adicionar campo tempo online humanizado
            player['human_onlinetime'] = humanize_time(player.get('onlinetime', 0))
        
        result = attach_crests_to_clans(result)
        context['ranking'] = result
        return context
    
    def get_title(self):
        return _('Top Online')


class TopsOlympiadView(TopsBaseView):
    template_name = 'tops/olympiad.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        db = LineageDB()
        result = LineageStats.olympiad_ranking() if db.is_connected() else []
        
        # Import get_class_name at the beginning of the method
        from utils.resources import get_class_name
        
        # Filtra registros com valores None
        filtered_result = []
        for player in result:
            # Só inclui se char_name não for None
            if player.get('char_name') is not None:
                filtered_result.append(player)
        
        # Aplicar filtros baseados nos parâmetros GET
        search_query = self.request.GET.get('search', '').strip().lower()
        class_filter = self.request.GET.get('class', '').strip()
        clan_filter = self.request.GET.get('clan', '').strip().lower()
        status_filter = self.request.GET.get('status', '').strip()
        min_points = self.request.GET.get('min_points', '').strip()
        
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
        
        # Processar os dados para incluir nome da classe
        for player in filtered_result:
            if 'base' in player and player['base'] is not None:
                player['class_name'] = get_class_name(player['base'])
            else:
                player['class_name'] = '-'
        
        # Preparar dados para os filtros
        all_classes = list(set([get_class_name(p.get('base', '')) for p in filtered_result if p.get('base')]))
        all_classes.sort()
        
        context['ranking'] = filtered_result
        context['filters'] = {
            'search': self.request.GET.get('search', ''),
            'class': self.request.GET.get('class', ''),
            'clan': self.request.GET.get('clan', ''),
            'status': self.request.GET.get('status', ''),
            'min_points': self.request.GET.get('min_points', ''),
        }
        context['available_classes'] = all_classes
        context['total_players'] = len(result)
        context['filtered_players'] = len(filtered_result)
        
        return context
    
    def get_title(self):
        return _('Ranking Olimpíada')


class TopsSiegeView(TopsBaseView):
    template_name = 'tops/siege.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            db = LineageDB()
            if db.is_connected():
                castles = LineageStats.siege()

                for castle in castles:
                    participants = LineageStats.siege_participants(castle["id"])
                    castle["siege_participants"] = participants

                    # adiciona caminho da imagem baseado no nome
                    castle_name_lower = castle['name'].lower()
                    # Mapeamento para garantir que as imagens sejam encontradas
                    castle_image_mapping = {
                        'aden': 'aden',
                        'dion': 'dion',
                        'giran': 'giran',
                        'gludio': 'gludio',
                        'goddard': 'goddard',
                        'innadril': 'innadril',
                        'oren': 'oren',
                        'rune': 'rune',
                        'schuttgart': 'schuttgart'
                    }
                    
                    image_name = castle_image_mapping.get(castle_name_lower, castle_name_lower)
                    castle["image_path"] = f"assets/img/castles/{image_name}.jpg"

                    # adiciona valores default traduzidos se vazio
                    castle["clan_name"] = castle["clan_name"] or _("No Owner")
                    castle["char_name"] = castle["char_name"] or _("No Leader")
                    castle["ally_name"] = castle["ally_name"] or _("No Alliance")

                    # CORREÇÃO AQUI: converte Decimal para float
                    if castle["sdate"]:
                        timestamp_s = float(castle["sdate"]) / 1000
                        castle["siege_date"] = datetime.fromtimestamp(timestamp_s)
                    
                    # Garantir que os participantes tenham valores padrão
                    for participant in castle["siege_participants"]:
                        participant["clan_name"] = participant["clan_name"] or _("Unknown Clan")

                # move para fora do loop para não sobrescrever a cada iteração
                castles = attach_crests_to_clans(castles)
                
                # Aplicar crests aos participantes também
                for castle in castles:
                    if castle.get("siege_participants"):
                        castle["siege_participants"] = attach_crests_to_clans(castle["siege_participants"])
            else:
                castles = list()
        except Exception as e:
            print(f"Erro ao carregar dados do siege: {e}")
            castles = list()

        context['castles'] = castles
        return context
    
    def get_title(self):
        return _('Castle & Siege Ranking')
