from rest_framework.decorators import api_view, throttle_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import AnonRateThrottle
from rest_framework.generics import GenericAPIView, ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import models
from datetime import datetime
import logging
from drf_spectacular.utils import extend_schema, OpenApiParameter, inline_serializer
from rest_framework import serializers

from .serializers import (
    PlayerOnlineSerializer, TopPlayerSerializer, TopClanSerializer,
    OlympiadRankingSerializer, OlympiadHeroSerializer, GrandBossStatusSerializer,
    SiegeSerializer, SiegeParticipantSerializer, BossJewelLocationSerializer,
    CustomTokenObtainPairSerializer, RefreshTokenSerializer, LoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer, CharacterSerializer,
    ItemSerializer, ClanDetailSerializer, AuctionItemSerializer,
    APIResponseSerializer, ServerStatusSerializer, DiscordServerSerializer,
    UserGameDataSerializer, ServerInfoSerializer, NewsSerializer
)
from apps.main.news.models import News
from rest_framework import generics, permissions
from .forms import ApiEndpointToggleForm
from .permissions import IsSuperUser, IsAPIAdmin, IsMonitoringAdmin

from .schema import ServerAPISchema, AuthAPISchema, UserAPISchema, SearchAPISchema, GameDataAPISchema, ServerStatusAPISchema, APIInfoSchema

from utils.dynamic_import import get_query_class
from utils.resources import get_class_name
from apps.lineage.server.utils.crest import attach_crests_to_clans
from apps.lineage.server.utils.bosses import enrich_grandboss_status, enrich_raidboss_status
from apps.lineage.server.decorators import endpoint_enabled
from apps.lineage.server.models import ApiEndpointToggle
from apps.main.notification.models import PushSubscription
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import DiscordServer

# Carrega a classe LineageStats baseada na configuração
LineageStats = get_query_class("LineageStats")


class PublicAPIRateThrottle(AnonRateThrottle):
    """Rate limit para APIs públicas: 30 requisições por minuto"""
    rate = '30/minute'


# =========================== SERVER INFO VIEW ===========================

class ServerInfoView(APIView):
    """
    Endpoint público com metadados do servidor PDL.
    Usado pelo PWA para personalizar nome, logo, descrição e social links.
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]

    @extend_schema(
        summary="Informações do Servidor",
        description="Retorna metadados públicos do servidor: nome, descrição, versão, redes sociais e configurações.",
        responses={200: ServerInfoSerializer},
        tags=["Servidor"],
        auth=[]
    )
    def get(self, request):
        """Retorna dados públicos do servidor para uso no PWA."""
        cache_key = 'api_server_info'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        # Obtém a crônica da configuração LINEAGE_QUERY_MODULE
        module = getattr(settings, 'LINEAGE_QUERY_MODULE', '')
        chronicle_map = {
            'dreamv3': 'Interlude',
            'l2dev': 'High Five',
            'l2jfrozen': 'Interlude',
            'lucera': 'Interlude',
        }
        chronicle = chronicle_map.get(module, module.capitalize() if module else '')

        data = {
            'name': getattr(settings, 'PROJECT_TITLE', 'PDL'),
            'short_name': getattr(settings, 'PROJECT_TITLE', 'PDL').split()[0] if getattr(settings, 'PROJECT_TITLE', '') else 'PDL',
            'description': getattr(settings, 'PROJECT_DESCRIPTION', ''),
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'chronicle': chronicle,
            'logo_url': getattr(settings, 'PROJECT_LOGO_URL', '/static/pwa/icons/logo.png'),
            'discord_url': getattr(settings, 'PROJECT_DISCORD_URL', ''),
            'youtube_url': getattr(settings, 'PROJECT_YOUTUBE_URL', ''),
            'facebook_url': getattr(settings, 'PROJECT_FACEBOOK_URL', ''),
            'instagram_url': getattr(settings, 'PROJECT_INSTAGRAM_URL', ''),
            'theme_color': getattr(settings, 'PROJECT_THEME_COLOR', '#0d0d0d'),
            'rates': {
                'xp': str(getattr(settings, 'XP_RATE', 'x1')),
                'sp': str(getattr(settings, 'SP_RATE', 'x1')),
                'drop': str(getattr(settings, 'DROP_RATE', 'x1')),
                'adena': str(getattr(settings, 'ADENA_RATE', 'x1')),
            },
            'features': {
                'payments': getattr(settings, 'MERCADO_PAGO_ACTIVATE_PAYMENTS', False) or getattr(settings, 'STRIPE_ACTIVATE_PAYMENTS', False),
                'push_notifications': bool(getattr(settings, 'VAPID_PUBLIC_KEY', None)),
                'discord_integration': getattr(settings, 'SOCIAL_LOGIN_DISCORD_ENABLED', False),
                'show_players_online': getattr(settings, 'SHOW_PLAYERS_ONLINE', True),
            },
        }

        serializer = ServerInfoSerializer(data)
        cache.set(cache_key, serializer.data, 300)  # Cache 5 minutos
        return Response(serializer.data)


@endpoint_enabled('players_online')
@ServerAPISchema.players_online_schema()
class PlayersOnlineView(GenericAPIView):
    """View para dados de jogadores online"""
    permission_classes = [AllowAny]
    serializer_class = PlayerOnlineSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o número de jogadores online
        """
        try:
            # Tenta buscar do cache primeiro
            cache_key = 'api_players_online'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Se não está em cache, busca dos dados
                data = LineageStats.players_online()
                # Cache por 30 segundos
                cache.set(cache_key, data, 30)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if not data or not isinstance(data, list) or len(data) == 0:
                return Response(
                    {'error': 'Dados de jogadores online não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Extrai o valor da consulta
            online_count = data[0].get('quant', 0) if data else 0
            
            # Prepara os dados para o serializer
            response_data = {
                'online_count': online_count,
                'fake_players': 0,  # Pode ser calculado baseado na configuração
                'real_players': online_count
            }
            
            serializer = self.get_serializer(response_data)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em players_online: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar dados de jogadores online: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_pvp')
@ServerAPISchema.top_pvp_schema()
class TopPvPView(GenericAPIView):
    """View para ranking PvP"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    @staticmethod
    def _humanize_time(seconds):
        """Formata tempo em segundos para formato legível (ex: 2d 5h 30m)"""
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
    
    def get(self, request):
        """
        Retorna o ranking PvP
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)  # Limita a 100 registros
            
            cache_key = f'api_top_pvp_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_pvp(limit=limit)
                # Aplica tradução de nomes de classe e mapeia campos
                for player in data:
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_name' not in player:
                        player['class_name'] = None
                    # Mapeia pvpkills para pvp_count
                    if 'pvpkills' in player:
                        player['pvp_count'] = player['pvpkills']
                    # Mapeia pkkills para pk_count
                    if 'pkkills' in player:
                        player['pk_count'] = player['pkkills']
                # Adiciona crests dos clãs
                data = attach_crests_to_clans(data)
                cache.set(cache_key, data, 60)  # Cache por 1 minuto
            else:
                data = cached_data
            
            # Mapeia campos do banco para o formato esperado pelo serializer (também quando vem do cache)
            for player in data:
                # Mapeia pvpkills para pvp_count
                if 'pvpkills' in player:
                    player['pvp_count'] = player['pvpkills']
                # Mapeia pkkills para pk_count
                if 'pkkills' in player:
                    player['pk_count'] = player['pkkills']
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking PvP'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_pk')
@ServerAPISchema.top_pk_schema()
class TopPKView(GenericAPIView):
    """View para ranking PK"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    @staticmethod
    def _humanize_time(seconds):
        """Formata tempo em segundos para formato legível (ex: 2d 5h 30m)"""
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
    
    def get(self, request):
        """
        Retorna o ranking PK
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_pk_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_pk(limit=limit)
                # Aplica tradução de nomes de classe e mapeia campos
                for player in data:
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_name' not in player:
                        player['class_name'] = None
                    # Mapeia pvpkills para pvp_count
                    if 'pvpkills' in player:
                        player['pvp_count'] = player['pvpkills']
                    # Mapeia pkkills para pk_count
                    if 'pkkills' in player:
                        player['pk_count'] = player['pkkills']
                # Adiciona crests dos clãs
                data = attach_crests_to_clans(data)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Mapeia campos do banco para o formato esperado pelo serializer
            for player in data:
                # Mapeia pvpkills para pvp_count
                if 'pvpkills' in player:
                    player['pvp_count'] = player['pvpkills']
                # Mapeia pkkills para pk_count
                if 'pkkills' in player:
                    player['pk_count'] = player['pkkills']
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking PK'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_clan')
@ServerAPISchema.top_clan_schema()
class TopClanView(GenericAPIView):
    """View para ranking de clãs"""
    permission_classes = [AllowAny]
    serializer_class = TopClanSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking de clãs
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_clan_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_clans(limit=limit)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if data is None:
                return Response(
                    {'error': 'Dados de clãs não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Processa os dados para garantir compatibilidade com o serializer
            processed_data = []
            for clan in data:
                processed_clan = {
                    'clan_name': clan.get('clan_name', ''),
                    'leader_name': clan.get('char_name', ''),
                    'level': clan.get('clan_level', 0),
                    'member_count': clan.get('membros', 0),
                    'reputation': clan.get('reputation_score', 0)
                }
                processed_data.append(processed_clan)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em top_clan: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar ranking de clãs: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_rich')
@ServerAPISchema.top_rich_schema()
class TopRichView(GenericAPIView):
    """View para ranking de riqueza"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    @staticmethod
    def _humanize_time(seconds):
        """Formata tempo em segundos para formato legível (ex: 2d 5h 30m)"""
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
    
    def get(self, request):
        """
        Retorna o ranking de riqueza (Adena)
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_rich_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_adena(limit=limit)
                # Padroniza campo adena (adenas -> adena) e mapeia campos
                for player in data:
                    if 'adenas' in player and 'adena' not in player:
                        player['adena'] = player['adenas']
                    # Formata tempo online humanizado
                    if 'onlinetime' in player:
                        player['human_onlinetime'] = self._humanize_time(player.get('onlinetime', 0))
                        # Mapeia onlinetime para online_time
                        player['online_time'] = player['onlinetime']
                # Aplica tradução de nomes de classe
                for player in data:
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_name' not in player:
                        player['class_name'] = None
                # Adiciona crests dos clãs
                data = attach_crests_to_clans(data)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Mapeia campos do banco para o formato esperado pelo serializer (também quando vem do cache)
            for player in data:
                # Mapeia onlinetime para online_time
                if 'onlinetime' in player and 'online_time' not in player:
                    player['online_time'] = player['onlinetime']
                # Garante que human_onlinetime existe se onlinetime existe
                if 'onlinetime' in player and 'human_onlinetime' not in player:
                    player['human_onlinetime'] = self._humanize_time(player.get('onlinetime', 0))
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking de riqueza'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_online')
@ServerAPISchema.top_online_schema()
class TopOnlineView(GenericAPIView):
    """View para ranking de tempo online"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    @staticmethod
    def _humanize_time(seconds):
        """Formata tempo em segundos para formato legível (ex: 2d 5h 30m)"""
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
    
    def get(self, request):
        """
        Retorna o ranking de tempo online
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_online_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_online(limit=limit)
                # Formata tempo online humanizado e mapeia campos
                for player in data:
                    if 'onlinetime' in player:
                        player['human_onlinetime'] = self._humanize_time(player.get('onlinetime', 0))
                        # Mapeia onlinetime para online_time
                        player['online_time'] = player['onlinetime']
                # Aplica tradução de nomes de classe
                for player in data:
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_name' not in player:
                        player['class_name'] = None
                # Adiciona crests dos clãs
                data = attach_crests_to_clans(data)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Mapeia campos do banco para o formato esperado pelo serializer (também quando vem do cache)
            for player in data:
                # Mapeia onlinetime para online_time
                if 'onlinetime' in player and 'online_time' not in player:
                    player['online_time'] = player['onlinetime']
                # Garante que human_onlinetime existe se onlinetime existe
                if 'onlinetime' in player and 'human_onlinetime' not in player:
                    player['human_onlinetime'] = self._humanize_time(player.get('onlinetime', 0))
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking de tempo online'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('top_level')
@ServerAPISchema.top_level_schema()
class TopLevelView(GenericAPIView):
    """View para ranking de nível"""
    permission_classes = [AllowAny]
    serializer_class = TopPlayerSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking de nível
        """
        try:
            limit = int(request.GET.get("limit", 10))
            limit = min(limit, 100)
            
            cache_key = f'api_top_level_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.top_level(limit=limit)
                # Aplica tradução de nomes de classe
                for player in data:
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_name' not in player:
                        player['class_name'] = None
                # Adiciona crests dos clãs
                data = attach_crests_to_clans(data)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar ranking de nível'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('olympiad_ranking')
@ServerAPISchema.olympiad_ranking_schema()
class OlympiadRankingView(GenericAPIView):
    """View para ranking da Olimpíada"""
    permission_classes = [AllowAny]
    serializer_class = OlympiadRankingSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o ranking da Olimpíada
        """
        try:
            cache_key = 'api_olympiad_ranking'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.olympiad_ranking()
                cache.set(cache_key, data, 300)  # Cache por 5 minutos
            else:
                data = cached_data
            
            # Filtra registros com valores None
            filtered_data = []
            for player in data:
                if player.get('char_name') is not None:
                    filtered_data.append(player)
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for i, player in enumerate(filtered_data, 1):
                processed_player = {
                    'char_name': player.get('char_name', ''),
                    'class_name': get_class_name(player.get('base')) if player.get('base') else '-',
                    'points': player.get('olympiad_points', 0),
                    'rank': i
                }
                processed_data.append(processed_player)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em olympiad_ranking: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar ranking da Olimpíada: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('olympiad_all_heroes')
@ServerAPISchema.olympiad_heroes_schema("Todos os Heróis", "Retorna todos os heróis da Olimpíada")
class OlympiadAllHeroesView(GenericAPIView):
    """View para todos os heróis da Olimpíada"""
    permission_classes = [AllowAny]
    serializer_class = OlympiadHeroSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna todos os heróis da Olimpíada
        """
        try:
            cache_key = 'api_olympiad_all_heroes'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.olympiad_all_heroes()
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            # Filtra registros com valores None e aplica tradução de nomes de classe
            filtered_data = []
            for player in data:
                if player.get('char_name') is not None:
                    # Aplica tradução de nomes de classe
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_id' in player and player.get('class_id') is not None:
                        player['class_name'] = get_class_name(player['class_id'])
                    filtered_data.append(player)
            
            serializer = self.get_serializer(filtered_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar heróis da Olimpíada'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('olympiad_current_heroes')
@ServerAPISchema.olympiad_heroes_schema("Heróis Atuais", "Retorna os heróis atuais da Olimpíada")
class OlympiadCurrentHeroesView(GenericAPIView):
    """View para heróis atuais da Olimpíada"""
    permission_classes = [AllowAny]
    serializer_class = OlympiadHeroSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna os heróis atuais da Olimpíada
        """
        try:
            cache_key = 'api_olympiad_current_heroes'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.olympiad_current_heroes()
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            # Filtra registros com valores None e aplica tradução de nomes de classe
            filtered_data = []
            for player in data:
                if player.get('char_name') is not None:
                    # Aplica tradução de nomes de classe
                    if 'base' in player and player.get('base') is not None:
                        player['class_name'] = get_class_name(player['base'])
                    elif 'class_id' in player and player.get('class_id') is not None:
                        player['class_name'] = get_class_name(player['class_id'])
                    filtered_data.append(player)
            
            serializer = self.get_serializer(filtered_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar heróis atuais da Olimpíada'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('grandboss_status')
@ServerAPISchema.grandboss_status_schema()
class GrandBossStatusView(GenericAPIView):
    """View para status dos Grand Bosses"""
    permission_classes = [AllowAny]
    serializer_class = GrandBossStatusSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o status dos Grand Bosses
        """
        try:
            cache_key = 'api_grandboss_status'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                raw_data = LineageStats.grandboss_status() if hasattr(LineageStats, 'grandboss_status') else []
                # Enriquece os dados de bosses (normaliza status, respawn, etc.)
                data = enrich_grandboss_status(raw_data)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if not data or not isinstance(data, list):
                return Response(
                    {'error': 'Dados de status dos Grand Bosses não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for boss in data:
                processed_boss = {
                    'boss_id': boss.get('boss_id', 0),
                    'boss_name': boss.get('name', 'Unknown'),
                    'is_alive': boss.get('is_alive', False),
                    'respawn_time': boss.get('respawn_human', '-'),
                    'location': boss.get('location', 'Unknown'),
                }
                processed_data.append(processed_boss)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em grandboss_status: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar status dos Grand Bosses: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('siege')
@ServerAPISchema.siege_schema()
class SiegeView(GenericAPIView):
    """View para status dos cercos"""
    permission_classes = [AllowAny]
    serializer_class = SiegeSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o status dos cercos
        """
        try:
            cache_key = 'api_siege'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.siege()
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for castle in data:
                # Converte timestamp para datetime se necessário
                siege_date = castle.get('sdate')
                if siege_date:
                    try:
                        # Se for um timestamp em milissegundos, converte para segundos
                        if isinstance(siege_date, (int, float)) and siege_date > 1000000000000:
                            siege_date = siege_date / 1000
                        
                        # Converte para datetime
                        from datetime import datetime
                        siege_date = datetime.fromtimestamp(siege_date)
                    except (ValueError, TypeError, OSError):
                        siege_date = None
                
                processed_castle = {
                    'castle_name': castle.get('name', ''),
                    'castle_id': castle.get('id', 0),
                    'owner_clan': castle.get('clan_name', ''),
                    'siege_date': siege_date,
                    'is_under_siege': bool(castle.get('sdate'))
                }
                processed_data.append(processed_castle)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em siege: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar dados dos cercos: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('siege_participants')
@ServerAPISchema.siege_participants_schema()
class SiegeParticipantsView(GenericAPIView):
    """View para participantes do cerco"""
    permission_classes = [AllowAny]
    serializer_class = SiegeParticipantSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request, castle_id):
        """
        Retorna os participantes de um cerco específico
        """
        try:
            if castle_id not in range(1, 10):
                return Response(
                    {'error': 'castle_id deve ser um valor entre 1 e 9'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cache_key = f'api_siege_participants_{castle_id}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.siege_participants(castle_id=castle_id)
                # Aplica tradução de nomes de classe se os dados contiverem informações de personagens
                if data and isinstance(data, list):
                    for participant in data:
                        if 'base' in participant and participant.get('base') is not None:
                            participant['class_name'] = get_class_name(participant['base'])
                        elif 'class_id' in participant and participant.get('class_id') is not None:
                            participant['class_name'] = get_class_name(participant['class_id'])
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            serializer = self.get_serializer(data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar participantes do cerco'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('boss_jewel_locations')
@ServerAPISchema.boss_jewel_locations_schema()
class BossJewelLocationsView(GenericAPIView):
    """View para localizações dos Boss Jewels"""
    permission_classes = [AllowAny]
    serializer_class = BossJewelLocationSerializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna as localizações dos Boss Jewels
        """
        try:
            jewel_ids = request.GET.get("ids", "")
            
            if not jewel_ids:
                return Response(
                    {"error": "Parâmetro 'ids' é obrigatório"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                jewel_ids_list = [int(id) for id in jewel_ids.split(',')]
            except ValueError:
                return Response(
                    {"error": "Formato de ID inválido"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # IDs de todas as joias de boss disponíveis
            # B-grade: 6660, 22174
            # A-grade: 6661, 8191, 6662
            # S-grade: 6656, 6657, 6658, 6659, 22173
            # S84-grade: 16025, 16026, 21712, 22175
            allowed_ids = [6656, 6657, 6658, 6659, 6660, 6661, 6662, 8191, 16025, 16026, 21712, 22173, 22174, 22175]
            if not all(id in allowed_ids for id in jewel_ids_list):
                return Response(
                    {"error": "ID(s) de jewel inválido(s)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cache_key = f'api_boss_jewel_locations_{jewel_ids}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                data = LineageStats.boss_jewel_locations(boss_jewel_ids=jewel_ids_list)
                cache.set(cache_key, data, 300)
            else:
                data = cached_data
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for jewel in data:
                # Mapeia IDs para nomes de jewels
                jewel_names = {
                    6656: "Antharas Jewel",
                    6657: "Valakas Jewel", 
                    6658: "Lindvior Jewel",
                    6659: "Frintezza Jewel",
                    6660: "Baium Jewel",
                    6661: "Queen Ant Jewel",
                    8191: "Core Jewel"
                }
                
                processed_jewel = {
                    'jewel_id': jewel.get('item_id', 0),
                    'jewel_name': jewel_names.get(jewel.get('item_id'), f"Jewel {jewel.get('item_id')}"),
                    'location': f"{jewel.get('char_name', 'Unknown')} ({jewel.get('clan_name', 'No Clan')})",
                    'coordinates': '',  # Não disponível nos dados
                    'respawn_time': None  # Não disponível nos dados
                }
                processed_data.append(processed_jewel)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro em boss_jewel_locations: {str(e)}", exc_info=True)
            return Response(
                {'error': f'Erro ao buscar localizações dos Boss Jewels: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('raidboss_status')
@ServerAPISchema.grandboss_status_schema()
class RaidBossStatusView(GenericAPIView):
    """View para status dos Raid Bosses"""
    permission_classes = [AllowAny]
    serializer_class = GrandBossStatusSerializer  # Reutiliza o mesmo serializer
    throttle_classes = [PublicAPIRateThrottle]
    queryset = ApiEndpointToggle.objects.none()  # Empty queryset for DRF Spectacular
    
    def get(self, request):
        """
        Retorna o status dos Raid Bosses
        """
        try:
            cache_key = 'api_raidboss_status'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                raw_data = LineageStats.raidboss_status() if hasattr(LineageStats, 'raidboss_status') else []
                # Enriquece os dados de bosses (normaliza status, respawn, etc.)
                data = enrich_raidboss_status(raw_data)
                cache.set(cache_key, data, 60)
            else:
                data = cached_data
            
            # Verifica se os dados estão no formato esperado
            if not data or not isinstance(data, list):
                return Response(
                    {'error': 'Dados de status dos Raid Bosses não disponíveis'},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )
            
            # Processa os dados para o formato esperado pelo serializer
            processed_data = []
            for boss in data:
                processed_boss = {
                    'boss_id': boss.get('boss_id', 0),
                    'boss_name': boss.get('name', 'Unknown'),
                    'is_alive': boss.get('is_alive', False),
                    'respawn_time': boss.get('respawn_human', '-'),
                    'location': boss.get('location', 'Unknown'),
                }
                processed_data.append(processed_boss)
            
            serializer = self.get_serializer(processed_data, many=True)
            return Response(serializer.data)
        
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar status dos Raid Bosses'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# =========================== AUTHENTICATION VIEWS ===========================

@endpoint_enabled('auth_login')
@AuthAPISchema.login_schema()
class LoginView(TokenObtainPairView):
    """View para login com JWT"""
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            # Valida se username e password foram fornecidos
            username = request.data.get('username')
            password = request.data.get('password')
            
            if not username or not password:
                return Response(
                    {'error': 'Username e password são obrigatórios'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Tenta fazer login
            response = super().post(request, *args, **kwargs)
            
            # Se chegou aqui, o login foi bem-sucedido
            # Adiciona informações extras à resposta
            if hasattr(response, 'data') and response.status_code == 200:
                response.data.update({
                    'message': 'Login realizado com sucesso',
                    'timestamp': timezone.now().isoformat(),
                })
            
            return response
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Erro no login: {str(e)}", exc_info=True)
            
            # Retorna erro mais específico
            error_message = 'Erro ao realizar login'
            if 'authentication' in str(e).lower() or 'credentials' in str(e).lower():
                error_message = 'Credenciais inválidas'
                return Response(
                    {'error': error_message},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Em desenvolvimento, mostra o erro completo. Em produção, apenas a mensagem genérica
            import sys
            error_detail = str(e)
            if settings.DEBUG:
                import traceback
                error_detail = traceback.format_exc()
            
            return Response(
                {'error': error_message, 'detail': error_detail},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('auth_refresh')
@AuthAPISchema.refresh_token_schema()
class RefreshTokenView(TokenRefreshView):
    """View para refresh de token JWT"""
    serializer_class = RefreshTokenSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            response.data.update({
                'message': 'Token atualizado com sucesso',
                'timestamp': timezone.now().isoformat(),
            })
            return response
        except Exception as e:
            return Response(
                {'error': 'Token inválido ou expirado'},
                status=status.HTTP_401_UNAUTHORIZED
            )


@endpoint_enabled('auth_logout')
@AuthAPISchema.logout_schema()
class LogoutView(APIView):
    """View para logout"""
    permission_classes = [IsAuthenticated]
    serializer_class = APIResponseSerializer
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'message': 'Logout realizado com sucesso',
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao realizar logout'},
                status=status.HTTP_400_BAD_REQUEST
            )


@endpoint_enabled('user_profile')
@UserAPISchema.user_profile_schema()
class UserProfileView(APIView):
    """View para perfil do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer
    
    def get(self, request):
        """Retorna o perfil do usuário logado"""
        try:
            user = request.user
            serializer = UserProfileSerializer(user)
            
            # Retorna dados diretamente para compatibilidade com o bot
            # O bot espera receber os dados diretamente, não dentro de um wrapper
            profile_data = serializer.data
            
            # Adiciona campos adicionais que podem ser úteis
            profile_data['username'] = user.username
            profile_data['email'] = user.email
            profile_data['date_joined'] = user.date_joined.isoformat() if user.date_joined else None
            profile_data['last_login'] = user.last_login.isoformat() if user.last_login else None
            
            return Response(profile_data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar perfil: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar perfil do usuário'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Atualiza o perfil do usuário"""
        try:
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Perfil atualizado com sucesso',
                    'data': serializer.data,
                    'timestamp': timezone.now().isoformat(),
                })
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao atualizar perfil'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('user_change_password')
@UserAPISchema.change_password_schema()
class ChangePasswordView(APIView):
    """View para mudança de senha"""
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        try:
            serializer = ChangePasswordSerializer(data=request.data)
            if serializer.is_valid():
                user = request.user
                if not user.check_password(serializer.validated_data['old_password']):
                    return Response(
                        {'error': 'Senha atual incorreta'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'Senha alterada com sucesso',
                    'timestamp': timezone.now().isoformat(),
                })
            return Response(
                {'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao alterar senha'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== GAME VIEWS ===========================

@endpoint_enabled('search_character')
@SearchAPISchema.character_search_schema()
class CharacterSearchView(APIView):
    """View para busca de personagens"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = CharacterSerializer
    
    def get(self, request):
        try:
            # O bot usa 'name' como parâmetro, mas a API espera 'q'
            query = request.GET.get('name', request.GET.get('q', '')).strip()
            if not query or len(query) < 2:
                return Response(
                    {'error': 'Query deve ter pelo menos 2 caracteres'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Busca personagens no banco de dados do jogo
            cache_key = f'api_character_search_{query}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Usa método da classe LineageStats
                data = LineageStats.search_characters(query, limit=20) if hasattr(LineageStats, 'search_characters') else []
                # Aplica tradução de nomes de classe
                for character in data:
                    if 'base' in character and character.get('base') is not None:
                        character['class_name'] = get_class_name(character['base'])
                    elif 'class_id' in character and character.get('class_id') is not None:
                        character['class_name'] = get_class_name(character['class_id'])
                cache.set(cache_key, data, 300)  # Cache por 5 minutos
            else:
                data = cached_data
            
            serializer = CharacterSerializer(data, many=True)
            # Retorna dados diretamente para compatibilidade com o bot
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar personagens'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('search_item')
@SearchAPISchema.item_search_schema()
class ItemSearchView(APIView):
    """View para busca de itens"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = ItemSerializer
    
    def get(self, request):
        try:
            # O bot usa 'name' como parâmetro, mas a API espera 'q'
            query = request.GET.get('name', request.GET.get('q', '')).strip()
            if not query or len(query) < 2:
                return Response(
                    {'error': 'Query deve ter pelo menos 2 caracteres'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            cache_key = f'api_item_search_{query}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Busca itens no modelo Django Item e no arquivo JSON
                from apps.lineage.games.models import Item
                from apps.lineage.inventory.utils.items import get_itens_json
                
                data = []
                query_lower = query.lower()
                
                # Busca no modelo Django
                items = Item.objects.filter(name__icontains=query)[:20]
                for item in items:
                    data.append({
                        'item_id': item.item_id,
                        'item_name': item.name,
                        'item_type': item.get_rarity_display() if hasattr(item, 'get_rarity_display') else 'Unknown',
                        'grade': item.rarity if hasattr(item, 'rarity') else None,
                        'enchant_level': item.enchant if hasattr(item, 'enchant') else 0,
                        'description': item.description if hasattr(item, 'description') else ''
                    })
                
                # Busca no arquivo JSON (se não encontrou muitos resultados)
                if len(data) < 20:
                    try:
                        itens_data = get_itens_json()
                        for item_id, item_info in itens_data.items():
                            if len(data) >= 20:
                                break
                            if isinstance(item_info, list) and len(item_info) > 0:
                                item_name = item_info[0]
                                if query_lower in item_name.lower():
                                    # Evita duplicatas
                                    if not any(d['item_id'] == int(item_id) for d in data):
                                        data.append({
                                            'item_id': int(item_id),
                                            'item_name': item_name,
                                            'item_type': 'Unknown',
                                            'grade': None,
                                            'enchant_level': 0,
                                            'description': ''
                                        })
                    except Exception:
                        pass  # Se der erro ao ler JSON, continua com o que já tem
                
                cache.set(cache_key, data, 600)  # Cache por 10 minutos
            else:
                data = cached_data
            
            serializer = ItemSerializer(data, many=True)
            # Retorna dados diretamente para compatibilidade com o bot
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar itens'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('clan_detail')
@GameDataAPISchema.clan_detail_schema()
class ClanDetailView(APIView):
    """View para detalhes de clã"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = ClanDetailSerializer
    
    def get(self, request, clan_name):
        try:
            cache_key = f'api_clan_detail_{clan_name}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Usa método da classe LineageStats
                data = LineageStats.get_clan_details(clan_name) if hasattr(LineageStats, 'get_clan_details') else None
                if data:
                    cache.set(cache_key, data, 300)  # Cache por 5 minutos
            else:
                data = cached_data
            
            if not data:
                return Response(
                    {'error': 'Clã não encontrado'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            serializer = ClanDetailSerializer(data)
            # Retorna dados diretamente para compatibilidade com o bot
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar dados do clã'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('auction_items')
@GameDataAPISchema.auction_items_schema()
class AuctionItemsView(APIView):
    """View para itens do leilão"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = AuctionItemSerializer
    
    def get(self, request):
        try:
            limit = int(request.GET.get("limit", 20))
            limit = min(limit, 100)
            
            cache_key = f'api_auction_items_{limit}'
            cached_data = cache.get(cache_key)
            
            if cached_data is None:
                # Busca itens do leilão
                data = LineageStats.get_auction_items(limit) if hasattr(LineageStats, 'get_auction_items') else []
                cache.set(cache_key, data, 60)  # Cache por 1 minuto
            else:
                data = cached_data
            
            serializer = AuctionItemSerializer(data, many=True)
            # Retorna dados diretamente para compatibilidade com o bot
            return Response(serializer.data)
        except ValueError:
            return Response(
                {'error': 'Parâmetro limit deve ser um número válido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar itens do leilão'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== USER DASHBOARD VIEWS ===========================

@endpoint_enabled('user_dashboard')
@UserAPISchema.user_dashboard_schema()
class UserDashboardView(APIView):
    """View para dashboard do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        try:
            user = request.user
            
            # Busca dados do usuário no jogo
            game_data = LineageStats.get_user_stats(user.username) if hasattr(LineageStats, 'get_user_stats') else {}
            
            # Retorna dados diretamente para compatibilidade com o bot
            dashboard_data = {
                'username': user.username,
                'email': user.email,
                'date_joined': user.date_joined.isoformat() if user.date_joined else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
            
            # Adiciona dados do jogo se disponíveis
            if game_data:
                dashboard_data.update(game_data)
            
            # Adiciona informações do servidor
            try:
                players_online = LineageStats.players_online()[0].get('quant', 0) if LineageStats.players_online() else 0
                dashboard_data['server_online'] = True
                dashboard_data['players_online'] = players_online
            except:
                dashboard_data['server_online'] = False
                dashboard_data['players_online'] = 0
            
            return Response(dashboard_data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar dashboard: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar dados do dashboard'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('user_stats')
@UserAPISchema.user_stats_schema()
class UserStatsView(APIView):
    """View para estatísticas do usuário"""
    permission_classes = [IsAuthenticated]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        try:
            user = request.user
            
            # Busca estatísticas do usuário usando LineageServices.find_chars
            from utils.dynamic_import import get_query_class
            LineageServices = get_query_class("LineageServices")
            
            characters = []
            if hasattr(LineageServices, 'find_chars'):
                try:
                    characters = LineageServices.find_chars(user.username) or []
                except:
                    characters = []
            
            # Calcula estatísticas agregadas
            characters_count = len(characters) if characters else 0
            total_level = 0
            total_online_time = 0
            total_pvp = 0
            total_pk = 0
            
            if characters:
                for char in characters:
                    # Soma níveis (usa base_level se disponível, senão level)
                    level = char.get('base_level') or char.get('level', 0)
                    if level:
                        try:
                            total_level += int(level)
                        except:
                            pass
                    
                    # Soma tempo online
                    onlinetime = char.get('onlinetime', 0)
                    if onlinetime:
                        try:
                            total_online_time += int(onlinetime)
                        except:
                            pass
                    
                    # Soma PvP
                    pvpkills = char.get('pvpkills', 0)
                    if pvpkills:
                        try:
                            total_pvp += int(pvpkills)
                        except:
                            pass
                    
                    # Soma PK
                    pkkills = char.get('pkkills', 0)
                    if pkkills:
                        try:
                            total_pk += int(pkkills)
                        except:
                            pass
            
            stats_data = {
                'username': user.username,
                'characters_count': characters_count,
                'total_level': total_level,
                'total_online_time': total_online_time,
                'total_pvp': total_pvp,
                'total_pk': total_pk,
            }
            
            # Retorna dados diretamente para compatibilidade com o bot
            return Response(stats_data)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao buscar stats: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar estatísticas do usuário'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== SERVER STATUS VIEWS ===========================

@endpoint_enabled('server_status')
@ServerStatusAPISchema.server_status_schema()
class ServerStatusView(APIView):
    """View para status do servidor"""
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    serializer_class = ServerStatusSerializer
    
    def get(self, request):
        status_data = {
            'server_name': getattr(settings, 'PROJECT_TITLE', 'Lineage 2 Server'),
            'status': 'offline',
            'players_online': 0,
            'max_players': 1000,
            'uptime': '',
            'last_update': timezone.now(),
            'version': getattr(settings, 'VERSION', '1.0.0'),
            'maintenance_mode': False,
        }
        try:
            game_server_status = LineageStats.check_server_status() if hasattr(LineageStats, 'check_server_status') else False
            if game_server_status:
                players = LineageStats.players_online()
                status_data['status'] = 'online'
                status_data['players_online'] = players[0].get('quant', 0) if players else 0
        except Exception:
            pass
        serializer = ServerStatusSerializer(status_data)
        return Response({
            'success': True,
            'data': serializer.data,
            'timestamp': timezone.now().isoformat(),
        })


# =========================== API INFO VIEWS ===========================

@endpoint_enabled('api_info')
@APIInfoSchema.api_info_schema()
class APIInfoView(APIView):
    """View para informações da API"""
    permission_classes = [AllowAny]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        try:
            api_info = {
                'name': 'Lineage 2 API',
                'version': getattr(settings, 'VERSION', '1.0.0'),
                'description': 'API pública para servidores de Lineage 2',
                'documentation': '/api/v1/schema/swagger/',
                'endpoints': {
                    'public': [
                        '/api/v1/server/status/',
                        '/api/v1/server/players-online/',
                        '/api/v1/search/character/',
                        '/api/v1/search/item/',
                        '/api/v1/clan/{name}/',
                        '/api/v1/auction/items/',
                    ],
                    'authenticated': [
                        '/api/v1/auth/login/',
                        '/api/v1/auth/refresh/',
                        '/api/v1/auth/logout/',
                        '/api/v1/user/profile/',
                        '/api/v1/user/dashboard/',
                        '/api/v1/user/stats/',
                    ]
                },
                'rate_limits': {
                    'anonymous': '30/minute',
                    'authenticated': '100/minute'
                }
            }
            
            return Response({
                'success': True,
                'data': api_info,
                'timestamp': timezone.now().isoformat(),
            })
        except Exception as e:
            return Response(
                {'error': 'Erro ao buscar informações da API'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# =========================== MONITORING VIEWS ===========================
# Health check não usa @endpoint_enabled para estar sempre disponível (load balancers, K8s, etc.)

@extend_schema(
    summary="Health Check",
    description="Verifica a saúde dos sistemas da API (banco, cache, servidor do jogo). Sempre acessível.",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_503_SERVICE_UNAVAILABLE: APIResponseSerializer,
    },
    tags=["Monitoramento"],
    auth=[]
)
class HealthCheckView(APIView):
    """View para health check da API - sempre ativa, independente de ApiEndpointToggle."""
    permission_classes = [AllowAny]
    serializer_class = APIResponseSerializer

    def get(self, request):
        """Executa verificação completa de saúde"""
        try:
            from .monitoring import HealthCheck

            health_status = HealthCheck.full_health_check()

            # 503 apenas se componentes críticos (DB ou cache) falharem
            if health_status["status"] == "healthy":
                return Response({
                    "success": True,
                    "data": health_status,
                    "timestamp": timezone.now().isoformat(),
                })
            return Response({
                "success": False,
                "data": health_status,
                "timestamp": timezone.now().isoformat(),
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        except Exception as e:
            return Response({
                "success": False,
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@endpoint_enabled('hourly_metrics')
@extend_schema(
    summary="Métricas da Última Hora",
    description="Retorna estatísticas da API da última hora",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Monitoramento"],
    auth=[]
)
class HourlyMetricsView(APIView):
    """View para métricas da última hora"""
    permission_classes = [IsAuthenticated]  # Apenas usuários autenticados
    
    def get(self, request):
        """Retorna métricas da última hora"""
        try:
            from .monitoring import APIMetrics
            
            # Verifica se o usuário é staff
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas administradores podem acessar métricas.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            metrics = APIMetrics.get_hourly_stats()
            
            return Response({
                'success': True,
                'data': metrics,
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erro ao buscar métricas: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@endpoint_enabled('daily_metrics')
@extend_schema(
    summary="Métricas do Dia",
    description="Retorna estatísticas da API do dia atual",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Monitoramento"],
    auth=[]
)
class DailyMetricsView(APIView):
    """View para métricas do dia"""
    permission_classes = [IsAuthenticated]  # Apenas usuários autenticados
    
    def get(self, request):
        """Retorna métricas do dia atual"""
        try:
            from .monitoring import APIMetrics
            
            # Verifica se o usuário é staff
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas administradores podem acessar métricas.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            metrics = APIMetrics.get_daily_stats()
            
            return Response({
                'success': True,
                'data': metrics,
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erro ao buscar métricas: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@endpoint_enabled('performance_metrics')
@extend_schema(
    summary="Performance por Endpoint",
    description="Retorna estatísticas de performance por endpoint",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Monitoramento"],
    auth=[]
)
class PerformanceMetricsView(APIView):
    """View para métricas de performance"""
    permission_classes = [IsAuthenticated]  # Apenas usuários autenticados
    
    def get(self, request):
        """Retorna métricas de performance por endpoint"""
        try:
            from .monitoring import APIPerformance
            
            # Verifica se o usuário é staff
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas administradores podem acessar métricas.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            performance = APIPerformance.get_endpoint_performance()
            
            return Response({
                'success': True,
                'data': performance,
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erro ao buscar métricas de performance: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@endpoint_enabled('slow_queries')
@extend_schema(
    summary="Queries Lentas",
    description="Retorna as queries mais lentas da API",
    parameters=[
        OpenApiParameter(
            name="limit",
            type=int,
            location=OpenApiParameter.QUERY,
            description="Número máximo de queries (padrão: 10)",
            default=10,
        )
    ],
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Monitoramento"],
    auth=[]
)
class SlowQueriesView(APIView):
    """View para queries lentas"""
    permission_classes = [IsAuthenticated]  # Apenas usuários autenticados
    
    def get(self, request):
        """Retorna as queries mais lentas"""
        try:
            from .monitoring import APIPerformance
            
            # Verifica se o usuário é staff
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas administradores podem acessar métricas.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            limit = int(request.GET.get('limit', 10))
            limit = min(limit, 50)  # Limita a 50 queries
            
            slow_queries = APIPerformance.get_slow_queries(limit)
            
            return Response({
                'success': True,
                'data': {
                    'slow_queries': slow_queries,
                    'count': len(slow_queries),
                    'limit': limit,
                },
                'timestamp': timezone.now().isoformat(),
            })
            
        except ValueError:
            return Response({
                'success': False,
                'error': 'Parâmetro limit deve ser um número válido',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erro ao buscar queries lentas: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =========================== API CONFIGURATION VIEWS ===========================

@endpoint_enabled('api_config')
@extend_schema(
    summary="API Endpoint Configuration",
    description="Configuração de endpoints da API (apenas para superusers)",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Administração"],
    auth=[]
)
class APIConfigView(APIView):
    """View para configuração de endpoints da API"""
    permission_classes = [IsSuperUser]
    serializer_class = APIResponseSerializer
    
    def get(self, request):
        """Retorna a configuração atual dos endpoints"""
        try:
            # Verifica se o usuário é superuser
            if not request.user.is_superuser:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas superusers podem acessar configurações.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            toggle, created = ApiEndpointToggle.objects.get_or_create(pk=1)
            
            # Usa o novo método do modelo para obter todos os endpoints
            config_data = toggle.get_all_endpoints()
            
            return Response({
                'success': True,
                'data': {
                    'endpoints': config_data,
                    'categories': toggle.get_endpoint_categories(),
                    'last_updated': toggle.updated_at.isoformat() if toggle.updated_at else None,
                },
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Erro ao buscar configuração: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Atualiza a configuração dos endpoints"""
        try:
            # Verifica se o usuário é superuser
            if not request.user.is_superuser:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas superusers podem modificar configurações.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            toggle, created = ApiEndpointToggle.objects.get_or_create(pk=1)
            
            # Obtém todos os campos booleanos do modelo
            all_endpoints = toggle.get_all_endpoints()
            endpoint_fields = list(all_endpoints.keys())
            
            # Atualiza os campos baseado nos dados recebidos
            updated_fields = []
            for field in endpoint_fields:
                if field in request.data:
                    # Converte o valor para boolean
                    new_value = bool(request.data[field])
                    current_value = getattr(toggle, field, False)
                    
                    if current_value != new_value:
                        setattr(toggle, field, new_value)
                        updated_fields.append(field)
            
            if updated_fields:
                toggle.save()
                
                # Limpa o cache relacionado aos endpoints alterados
                from django.core.cache import cache
                for field in updated_fields:
                    cache_key = f'api_{field}'
                    cache.delete(cache_key)
                
                # Log da ação
                logger = logging.getLogger(__name__)
                logger.info(f"API config updated by {request.user.username}: {updated_fields}")
            
            return Response({
                'success': True,
                'message': f'Configuração atualizada com sucesso. {len(updated_fields)} campo(s) alterado(s).',
                'data': {
                    'updated_fields': updated_fields,
                    'updated_count': len(updated_fields),
                    'last_updated': toggle.updated_at.isoformat() if toggle.updated_at else None,
                    'endpoints': toggle.get_all_endpoints(),
                },
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating API config: {e}")
            return Response({
                'success': False,
                'error': f'Erro ao atualizar configuração: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@endpoint_enabled('api_config_panel')
@extend_schema(
    summary="API Configuration Panel",
    description="Painel de configuração da API para superusers (interface HTML)",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
        status.HTTP_403_FORBIDDEN: APIResponseSerializer,
    },
    tags=["Administração"],
    auth=[]
)
class APIConfigPanelView(APIView):
    """View para painel de configuração da API (interface HTML)"""
    permission_classes = [IsSuperUser]
    serializer_class = APIResponseSerializer  # Adiciona serializer para DRF Spectacular
    
    def get(self, request):
        """Renderiza o painel de configuração HTML"""
        try:
            # Log de debug
            logger = logging.getLogger(__name__)
            logger.info(f"APIConfigPanelView accessed by user: {request.user.username}")
            
            # Verifica se o usuário é superuser
            if not request.user.is_superuser:
                logger.warning(f"Non-superuser {request.user.username} tried to access config panel")
                from django.shortcuts import render
                return render(request, "errors/403.html", status=403)
            
            # Busca dados de configuração para passar ao template
            try:
                logger.info("Attempting to get ApiEndpointToggle object")
                toggle, created = ApiEndpointToggle.objects.get_or_create(pk=1)
                logger.info(f"ApiEndpointToggle object {'created' if created else 'retrieved'}")
                
                # Cria o formulário com os dados atuais
                form = ApiEndpointToggleForm(instance=toggle)
                
                logger.info(f"Form created with {len(form.fields)} fields")
                
                context = {
                    'form': form,
                    'toggle': toggle,
                    'categories': toggle.get_endpoint_categories(),
                    'last_updated': toggle.updated_at if toggle.updated_at else None,
                    'user': request.user,
                }
                
                logger.info("Context prepared successfully")
                
            except Exception as e:
                logger.error(f"Error preparing context: {str(e)}", exc_info=True)
                context = {
                    'form': None,
                    'toggle': None,
                    'categories': {},
                    'last_updated': None,
                    'user': request.user,
                    'error': str(e),
                }
            
            from django.shortcuts import render
            logger.info("Rendering template")
            return render(request, "api/config.html", context)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error in APIConfigPanelView.get: {str(e)}", exc_info=True)
            from django.shortcuts import render
            return render(request, "errors/500.html", status=500)
    
    def post(self, request):
        """Atualiza a configuração via AJAX"""
        try:
            # Verifica se o usuário é superuser
            if not request.user.is_superuser:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas superusers podem modificar configurações.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            toggle, created = ApiEndpointToggle.objects.get_or_create(pk=1)
            
            # Cria o formulário com os dados da requisição
            form = ApiEndpointToggleForm(request.POST, instance=toggle)
            
            if form.is_valid():
                # Salva o formulário
                form.save()
                
                # Obtém os campos que foram alterados
                changed_data = form.changed_data
                
                if changed_data:
                    # Limpa o cache relacionado aos endpoints alterados
                    from django.core.cache import cache
                    for field in changed_data:
                        cache_key = f'api_{field}'
                        cache.delete(cache_key)
                    
                    # Log da ação
                    logger = logging.getLogger(__name__)
                    logger.info(f"API config updated by {request.user.username}: {changed_data}")
                
                # Verifica se é uma requisição AJAX
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    # Retorna JSON para requisições AJAX
                    return Response({
                        'success': True,
                        'message': f'Configuração atualizada com sucesso. {len(changed_data)} campo(s) alterado(s).',
                        'data': {
                            'updated_fields': changed_data,
                            'updated_count': len(changed_data),
                            'last_updated': toggle.updated_at.isoformat() if toggle.updated_at else None,
                            'endpoints': toggle.get_all_endpoints(),
                        },
                        'timestamp': timezone.now().isoformat(),
                    })
                else:
                    # Retorna o painel HTML atualizado
                    from django.shortcuts import render
                    from django.contrib import messages
                    
                    # Adiciona mensagem de sucesso
                    messages.success(request, f'Configuração atualizada com sucesso. {len(changed_data)} campo(s) alterado(s).')
                    
                    # Prepara o contexto atualizado
                    context = {
                        'form': form,
                        'toggle': toggle,
                        'categories': toggle.get_endpoint_categories(),
                        'last_updated': toggle.updated_at if toggle.updated_at else None,
                        'user': request.user,
                    }
                    
                    return render(request, "api/config.html", context)
            else:
                # Formulário inválido
                error_message = "Erro de validação: " + ", ".join([f"{field}: {', '.join(errors)}" for field, errors in form.errors.items()])
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return Response({
                        'success': False,
                        'error': error_message,
                        'timestamp': timezone.now().isoformat(),
                    }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    from django.shortcuts import render
                    from django.contrib import messages
                    
                    messages.error(request, error_message)
                    
                    context = {
                        'form': form,
                        'toggle': toggle,
                        'categories': toggle.get_endpoint_categories(),
                        'last_updated': toggle.updated_at if toggle.updated_at else None,
                        'user': request.user,
                    }
                    
                    return render(request, "api/config.html", context)
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating API config: {e}")
            
            # Verifica se é uma requisição AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return Response({
                    'success': False,
                    'error': f'Erro ao atualizar configuração: {str(e)}',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Retorna o painel HTML com mensagem de erro
                from django.shortcuts import render
                from django.contrib import messages
                
                messages.error(request, f'Erro ao atualizar configuração: {str(e)}')
                
                toggle, created = ApiEndpointToggle.objects.get_or_create(pk=1)
                config_data = toggle.get_all_endpoints()
                context = {
                    'config_data': config_data,
                    'categories': toggle.get_endpoint_categories(),
                    'last_updated': toggle.updated_at if toggle.updated_at else None,
                    'user': request.user,
                }
                
                return render(request, "api/config.html", context)
    
    def put(self, request):
        """Atualiza configuração específica"""
        return self.post(request)
    
    def delete(self, request):
        """Reseta configuração para padrões"""
        try:
            # Verifica se o usuário é staff
            if not request.user.is_staff:
                return Response({
                    'success': False,
                    'error': 'Acesso negado. Apenas administradores podem resetar configurações.',
                    'timestamp': timezone.now().isoformat(),
                }, status=status.HTTP_403_FORBIDDEN)
            
            toggle, created = ApiEndpointToggle.objects.get_or_create(pk=1)
            
            # Obtém todos os campos booleanos do modelo
            all_endpoints = toggle.get_all_endpoints()
            endpoint_fields = list(all_endpoints.keys())
            
            reset_fields = []
            for field in endpoint_fields:
                current_value = getattr(toggle, field, True)
                if current_value != True:
                    setattr(toggle, field, True)
                    reset_fields.append(field)
            
            if reset_fields:
                toggle.save()
                
                # Limpa todo o cache da API
                from django.core.cache import cache
                cache.clear()
                
                logger = logging.getLogger(__name__)
                logger.info(f"API config reset by {request.user.username}")
            
            return Response({
                'success': True,
                'message': 'Configuração resetada para padrões com sucesso.',
                'data': {
                    'reset_fields': reset_fields,
                    'reset_count': len(reset_fields),
                    'last_updated': toggle.updated_at.isoformat() if toggle.updated_at else None,
                    'endpoints': toggle.get_all_endpoints(),
                },
                'timestamp': timezone.now().isoformat(),
            })
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error resetting API config: {e}")
            return Response({
                'success': False,
                'error': f'Erro ao resetar configuração: {str(e)}',
                'timestamp': timezone.now().isoformat(),
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# =========================== REDIRECT VIEWS ===========================

@extend_schema(
    summary="API Landing Page",
    description="Página inicial da API com links para documentação e informações",
    responses={
        status.HTTP_200_OK: APIResponseSerializer,
    },
    tags=["Documentação"],
    auth=[]
)
class APIRedirectView(APIView):
    """View para landing page da API"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Retorna informações da API e links para documentação"""
        
        # Inspeciona as URLs reais da API para contar endpoints
        from django.urls import get_resolver
        from rest_framework.permissions import AllowAny
        from rest_framework.views import APIView
        
        resolver = get_resolver()
        api_endpoints = set()
        public_count = 0
        auth_count = 0
        admin_count = 0
        
        def explore_patterns(patterns, prefix=''):
            nonlocal public_count, auth_count, admin_count
            for pattern in patterns:
                if hasattr(pattern, 'url_patterns'):
                    explore_patterns(pattern.url_patterns, prefix + str(pattern.pattern))
                elif hasattr(pattern, 'callback'):
                    url_path = prefix + str(pattern.pattern)
                    # Filtra apenas URLs que começam com api/v1/ (ou similar que seja da API)
                    if 'api/' in url_path and 'swagger' not in url_path and 'redoc' not in url_path:
                        # Evita contar a mesma URL várias vezes (ex: com format suffix)
                        clean_url = url_path.replace('(?P<format>[a-z0-9]+)/?$', '')
                        if clean_url not in api_endpoints:
                            api_endpoints.add(clean_url)
                            
                            # Tenta descobrir permissões
                            callback = pattern.callback
                            is_public = False
                            
                            if hasattr(callback, 'view_class') and issubclass(callback.view_class, APIView):
                                view_class = callback.view_class
                                permissions = getattr(view_class, 'permission_classes', [])
                                if AllowAny in permissions:
                                    is_public = True
                                    
                            if is_public:
                                public_count += 1
                            else:
                                if 'admin' in clean_url or 'metrics' in clean_url:
                                    admin_count += 1
                                else:
                                    auth_count += 1

        try:
            explore_patterns(resolver.url_patterns)
        except Exception as e:
            # Fallback seguro caso dê erro na reflexão de URLs
            logger.warning(f"Erro ao contar endpoints da API: {e}")
            public_count = 25
            auth_count = 15
            admin_count = 5
        
        # Informações da API
        api_info = {
            'name': 'Lineage 2 API',
            'version': 'v1',
            'description': 'API pública para servidores de Lineage 2',
            'status': 'active',
            'documentation': {
                'swagger_ui': '/api/v1/schema/swagger/',
                'openapi_schema': '/api/v1/schema/',
                'redoc': '/api/v1/schema/redoc/',
            },
            'counts': {
                'public': public_count,
                'authenticated': auth_count,
                'admin_only': admin_count
            },
            'rate_limits': {
                'anonymous': '30/minute',
                'authenticated': '100/minute'
            },
            'features': [
                'Versionamento da API',
                'Paginação avançada',
                'Filtros robustos',
                'Cache inteligente',
                'Monitoramento em tempo real',
                'Documentação automática',
                'Rate limiting',
                'Health checks',
            ]
        }
        
        # Se a requisição aceita HTML, retorna o template
        if 'text/html' in request.META.get('HTTP_ACCEPT', ''):
            from django.shortcuts import render
            from django.conf import settings
            return render(request, 'api/gateway.html', {
                'api_info': api_info,
                'settings': settings
            })
        
        # Caso contrário, retorna JSON
        return Response({
            'success': True,
            'data': api_info,
            'timestamp': timezone.now().isoformat(),
        })


@extend_schema(
    summary="Chave Pública VAPID",
    description="Retorna a chave pública VAPID necessária para registrar uma assinatura push no browser.\n\nO cliente deve usar esta chave ao chamar `PushManager.subscribe()` no Service Worker.\n\n**Público** — não requer autenticação.",
    responses={200: APIResponseSerializer},
    tags=["Push"],
    auth=[]
)
class VapidPublicKeyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        from django.conf import settings
        return Response({"vapid_public_key": settings.VAPID_PUBLIC_KEY})


@extend_schema(
    summary="Inscrever Dispositivo Para Push 🔒",
    description="Registra a assinatura de push notification do dispositivo do usuário autenticado.\n\nEnvie o objeto de assinatura gerado pelo browser (endpoint, keys.auth, keys.p256dh).\n\nRequer token JWT no header.",
    tags=["Push"],
    request=inline_serializer(
        name="PushSubscriptionRequest",
        fields={
            'endpoint': serializers.URLField(required=True),
            'keys': inline_serializer(
                name="PushSubscriptionKeys",
                fields={
                    'auth': serializers.CharField(required=True),
                    'p256dh': serializers.CharField(required=True),
                }
            )
        }
    ),
    responses={
        200: inline_serializer(
            name="PushSubscriptionResponse",
            fields={
                'ok': serializers.BooleanField(),
                'deleted': serializers.IntegerField(required=False)
            }
        ),
        400: APIResponseSerializer
    }
)
class PushSubscriptionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        endpoint = data.get('endpoint')
        keys = data.get('keys', {})
        auth = keys.get('auth')
        p256dh = keys.get('p256dh')
        if not (endpoint and auth and p256dh):
            return Response({'error': 'Dados incompletos'}, status=status.HTTP_400_BAD_REQUEST)
        # Remove subscriptions antigas do mesmo endpoint
        PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        PushSubscription.objects.create(
            user=request.user,
            endpoint=endpoint,
            auth=auth,
            p256dh=p256dh
        )
        return Response({'ok': True})

    def delete(self, request):
        data = request.data
        endpoint = data.get('endpoint')
        if not endpoint:
            return Response({'error': 'Endpoint não informado'}, status=status.HTTP_400_BAD_REQUEST)
        deleted, _ = PushSubscription.objects.filter(user=request.user, endpoint=endpoint).delete()
        if deleted:
            return Response({'ok': True, 'deleted': deleted})
        else:
            return Response({'error': 'Inscrição não encontrada'}, status=status.HTTP_404_NOT_FOUND)


# =========================== DISCORD BOT ENDPOINTS ===========================

@extend_schema(
    summary="Informações do Servidor Discord",
    description="Retorna informações do servidor Discord cadastrado para este site PDL.\n\nUsado pelo bot do Discord para identificar a instância do site vinculada a um servidor Discord.\n\n**Público** — não requer autenticação.",
    tags=["Discord"],
    auth=[]
)
class DiscordServerView(APIView):
    """
    Endpoint para o bot Discord consultar informações de servidores cadastrados
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    
    @extend_schema(
        summary="Obter informações do servidor Discord",
        description="Retorna informações do servidor Discord pelo discord_guild_id.",
        parameters=[
            OpenApiParameter(
                name='discord_guild_id',
                type=str,
                location=OpenApiParameter.QUERY,
                description='ID do servidor Discord (ex: 1101010101100)',
                required=True
            )
        ],
        responses={200: DiscordServerSerializer, 404: None},
        tags=["Discord"],
    )
    def get(self, request):
        """Busca servidor Discord pelo ID"""
        discord_guild_id = request.query_params.get('discord_guild_id')
        
        if not discord_guild_id:
            return Response(
                {'error': 'discord_guild_id é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            discord_guild_id = int(discord_guild_id)
        except ValueError:
            return Response(
                {'error': 'discord_guild_id deve ser um número'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            server = DiscordServer.objects.get(
                discord_guild_id=discord_guild_id,
                is_active=True
            )
            serializer = DiscordServerSerializer(server)
            return Response(serializer.data)
        except DiscordServer.DoesNotExist:
            return Response(
                {'error': 'Servidor Discord não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erro ao buscar servidor Discord: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@endpoint_enabled('user_game_data')
class UserGameDataView(APIView):
    """
    Endpoint para obter dados de XP, conquistas e jogos do usuário
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    
    @UserAPISchema.user_game_data_schema()
    def get(self, request):
        """Busca dados de XP e conquistas do usuário"""
        from apps.main.home.models import PerfilGamer, Conquista, ConquistaUsuario, User
        from apps.lineage.games.models import UserBattlePassProgress, BattlePassSeason
        
        username = request.query_params.get('username')
        
        if not username:
            return Response(
                {'error': 'username é obrigatório'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuário não encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Busca ou cria PerfilGamer
        perfil_gamer, _ = PerfilGamer.objects.get_or_create(
            user=user,
            defaults={'xp': 0, 'level': 1}
        )
        
        # Conta conquistas
        total_achievements = Conquista.objects.count()
        user_achievements = ConquistaUsuario.objects.filter(usuario=user).count()
        
        # Busca dados do Battle Pass (se houver temporada ativa)
        battle_pass_xp = None
        battle_pass_level = None
        active_season = BattlePassSeason.objects.filter(is_active=True).first()
        if active_season:
            try:
                progress = UserBattlePassProgress.objects.get(
                    user=user,
                    season=active_season
                )
                battle_pass_xp = progress.xp
                current_level = progress.get_current_level()
                battle_pass_level = current_level.level if current_level else 0
            except UserBattlePassProgress.DoesNotExist:
                pass
        
        # Conta jogos (pode ser expandido depois)
        games_played = 0
        # Exemplo: contar spins, boxes abertas, etc.
        from apps.lineage.games.models import SpinHistory, Box
        games_played = (
            SpinHistory.objects.filter(user=user).count() +
            Box.objects.filter(user=user, opened=True).count()
        )
        
        # Calcula posição no ranking de XP do PDL
        # Ordena por XP decrescente, depois por ID crescente (desempate)
        # Conta quantos perfis estão à frente deste no ranking
        xp_ranking_position = (
            PerfilGamer.objects
            .filter(
                models.Q(xp__gt=perfil_gamer.xp) |
                models.Q(xp=perfil_gamer.xp, user__id__lt=user.id)
            )
            .count() + 1
        )
        
        # Prepara dados
        data = {
            'username': user.username,
            'level': perfil_gamer.level,
            'xp': perfil_gamer.xp,
            'xp_for_next_level': perfil_gamer.xp_para_proximo_nivel(),
            'achievements_count': user_achievements,
            'total_achievements': total_achievements,
            'battle_pass_xp': battle_pass_xp,
            'battle_pass_level': battle_pass_level,
            'games_played': games_played,
            'fichas': user.fichas,
            'xp_ranking_position': xp_ranking_position,
        }
        
        serializer = UserGameDataSerializer(data)
        return Response(serializer.data)


class DiscordServerByDomainView(APIView):
    """
    Endpoint para verificar se um domínio tem servidor Discord cadastrado
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicAPIRateThrottle]
    
    @extend_schema(
        summary="Verificar servidor Discord por domínio",
        description="Verifica se existe um servidor Discord cadastrado para este domínio.\n\n**Público** — não requer autenticação.",
        responses={200: DiscordServerSerializer, 404: None},
        tags=["Discord"],
        auth=[]
    )
    def get(self, request):
        """Busca servidor Discord pelo domínio atual"""
        # Obter o domínio da requisição
        host = request.get_host()
        domain = host.split(':')[0]  # Remove porta se houver
        
        try:
            server = DiscordServer.objects.get(
                site_domain=domain,
                is_active=True
            )
            serializer = DiscordServerSerializer(server)
            return Response(serializer.data)
        except DiscordServer.DoesNotExist:
            return Response(
                {'error': 'Nenhum servidor Discord cadastrado para este domínio'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Erro ao buscar servidor Discord por domínio: {e}", exc_info=True)
            return Response(
                {'error': 'Erro ao buscar servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== GAME SUMMARY VIEW ===========================

@endpoint_enabled('game_summary')
@extend_schema(
    summary="Resumo de Jogo do Usuário",
    description="Retorna wallet, itens da loja, conquistas, Battle Pass e jogos do usuário autenticado.",
    responses={200: APIResponseSerializer},
    tags=["Jogo"],
)
class GameSummaryView(APIView):
    """
    Retorna um resumo dos dados de jogo do usuário logado:
    wallet (saldo + bônus), itens da loja, últimas compras e dados de leilão.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {}

        # --- Wallet ---
        try:
            from apps.lineage.wallet.models import Wallet
            wallet = Wallet.objects.filter(usuario=user).first()
            if wallet:
                data['wallet'] = {
                    'saldo': float(wallet.saldo),
                    'saldo_bonus': float(wallet.saldo_bonus),
                    'total': float(wallet.saldo + wallet.saldo_bonus),
                }
            else:
                data['wallet'] = {'saldo': 0.0, 'saldo_bonus': 0.0, 'total': 0.0}
        except Exception:
            data['wallet'] = {'saldo': 0.0, 'saldo_bonus': 0.0, 'total': 0.0}

        # --- Loja ---
        try:
            from apps.lineage.shop.models import ShopItem
            shop_items = ShopItem.objects.filter(ativo=True).order_by('preco')[:8]
            data['shop_items'] = [
                {
                    'id': item.id,
                    'nome': item.nome,
                    'item_id': item.item_id,
                    'preco': float(item.preco),
                    'quantidade': item.quantidade,
                }
                for item in shop_items
            ]
        except Exception:
            data['shop_items'] = []

        # --- Fichas ---
        try:
            data['fichas'] = user.fichas if hasattr(user, 'fichas') else 0
        except Exception:
            data['fichas'] = 0

        # --- Conquistas ---
        try:
            from apps.main.home.models import ConquistaUsuario, Conquista
            total_achievements = Conquista.objects.count()
            user_achievements = ConquistaUsuario.objects.filter(usuario=user).count()
            data['achievements'] = {
                'count': user_achievements,
                'total': total_achievements,
                'pct': round((user_achievements / total_achievements * 100) if total_achievements else 0, 1),
            }
        except Exception:
            data['achievements'] = {'count': 0, 'total': 0, 'pct': 0}

        # --- Battle Pass ---
        try:
            from apps.lineage.games.models import BattlePassSeason, UserBattlePassProgress
            active_season = BattlePassSeason.objects.filter(is_active=True).first()
            if active_season:
                try:
                    progress = UserBattlePassProgress.objects.get(user=user, season=active_season)
                    current_level = progress.get_current_level()
                    data['battle_pass'] = {
                        'season_name': active_season.name,
                        'xp': progress.xp,
                        'level': current_level.level if current_level else 0,
                        'is_active': True,
                    }
                except UserBattlePassProgress.DoesNotExist:
                    data['battle_pass'] = {'season_name': active_season.name, 'xp': 0, 'level': 0, 'is_active': True}
            else:
                data['battle_pass'] = None
        except Exception:
            data['battle_pass'] = None

        # --- Jogos (giros, boxes) ---
        try:
            from apps.lineage.games.models import SpinHistory, Box
            spins = SpinHistory.objects.filter(user=user).count()
            boxes = Box.objects.filter(user=user, opened=True).count()
            data['games'] = {'spins': spins, 'boxes_opened': boxes, 'total': spins + boxes}
        except Exception:
            data['games'] = {'spins': 0, 'boxes_opened': 0, 'total': 0}

        return Response({'success': True, 'data': data, 'timestamp': timezone.now().isoformat()})


# =========================== GAME LEADERBOARD PDL ===========================

@endpoint_enabled('game_leaderboard')
@extend_schema(
    summary="Ranking PDL de XP",
    description="Retorna o top 20 de usuários ordenados por XP no sistema PDL. Cache de 2 minutos.",
    responses={200: APIResponseSerializer},
    tags=["Jogo"],
)
class GameLeaderboardView(APIView):
    """
    Retorna o ranking de XP e nível dos usuários no sistema PDL.
    Não requer dados do servidor de jogo — usa apenas dados do banco PDL.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = 'api_game_leaderboard'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        try:
            from apps.main.home.models import PerfilGamer
            top_players = (
                PerfilGamer.objects
                .select_related('user')
                .order_by('-xp')[:20]
            )
            ranking = [
                {
                    'position': i + 1,
                    'username': p.user.username,
                    'level': p.level,
                    'xp': p.xp,
                }
                for i, p in enumerate(top_players)
            ]
            result = {
                'success': True,
                'data': ranking,
                'timestamp': timezone.now().isoformat(),
            }
            cache.set(cache_key, result, 120)  # 2 minutos
            return Response(result)
        except Exception as e:
            return Response(
                {'success': False, 'error': str(e), 'data': []},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# =========================== ADMIN DASHBOARD VIEW ===========================

@endpoint_enabled('admin_dashboard')
@extend_schema(
    summary="Painel Admin (PWA)",
    description="Retorna estatísticas de usuários, push subscriptions, carteiras e configuração de endpoints. Requer is_staff=True.",
    responses={200: APIResponseSerializer, 403: APIResponseSerializer},
    tags=["Administração"],
)
class AdminDashboardView(APIView):
    """
    Painel de administração para staff — estatísticas de usuários,
    subscriptions de push e dados do sistema.
    Requer is_staff=True.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(
                {'success': False, 'error': 'Acesso negado. Apenas staff pode acessar o painel admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        cache_key = f'api_admin_dashboard_{request.user.id}'
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        data = {}

        # --- Usuários ---
        try:
            from apps.main.home.models import User
            from django.utils import timezone as tz
            from datetime import timedelta
            now = tz.now()
            data['users'] = {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'staff': User.objects.filter(is_staff=True).count(),
                'last_7_days': User.objects.filter(date_joined__gte=now - timedelta(days=7)).count(),
                'last_30_days': User.objects.filter(date_joined__gte=now - timedelta(days=30)).count(),
                'online_today': User.objects.filter(last_login__date=now.date()).count(),
            }
        except Exception:
            data['users'] = {}

        # --- Push Subscriptions ---
        try:
            from apps.main.notification.models import PushSubscription
            data['push'] = {
                'total_subscriptions': PushSubscription.objects.count(),
                'active_subscriptions': PushSubscription.objects.filter(active=True).count() if hasattr(PushSubscription, 'active') else PushSubscription.objects.count(),
            }
        except Exception:
            data['push'] = {'total_subscriptions': 0, 'active_subscriptions': 0}

        # --- Wallet summary ---
        try:
            from apps.lineage.wallet.models import Wallet
            from django.db.models import Sum, Count
            wallet_agg = Wallet.objects.aggregate(
                total_saldo=Sum('saldo'),
                total_bonus=Sum('saldo_bonus'),
                count=Count('id'),
            )
            data['wallet'] = {
                'total_wallets': wallet_agg['count'] or 0,
                'total_saldo': float(wallet_agg['total_saldo'] or 0),
                'total_bonus': float(wallet_agg['total_bonus'] or 0),
            }
        except Exception:
            data['wallet'] = {}

        # --- Endpoint config ---
        try:
            toggle, _ = ApiEndpointToggle.objects.get_or_create(pk=1)
            all_ep = toggle.get_all_endpoints()
            active_count = sum(1 for v in all_ep.values() if v)
            data['api_config'] = {
                'total_endpoints': len(all_ep),
                'active_endpoints': active_count,
                'inactive_endpoints': len(all_ep) - active_count,
                'last_updated': toggle.updated_at.isoformat() if toggle.updated_at else None,
                'endpoints': all_ep,
            }
        except Exception:
            data['api_config'] = {}

        # --- System info ---
        import sys
        import platform
        data['system'] = {
            'python_version': sys.version.split()[0],
            'platform': platform.system(),
            'debug': getattr(settings, 'DEBUG', False),
            'version': getattr(settings, 'VERSION', '—'),
        }

        result = {'success': True, 'data': data, 'timestamp': timezone.now().isoformat()}
        cache.set(cache_key, result, 60)  # 1 minuto
        return Response(result)


class NewsListView(generics.ListAPIView):
    """View para listar as notícias mais recentes do servidor"""
    queryset = News.objects.all().order_by('-created_at')[:5]
    serializer_class = NewsSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

