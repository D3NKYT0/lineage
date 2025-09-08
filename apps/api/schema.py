from drf_spectacular.extensions import OpenApiViewExtension
from drf_spectacular.plumbing import build_basic_type, build_parameter_type
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import status
from .serializers import (
    PlayerOnlineSerializer, TopPlayerSerializer, TopClanSerializer,
    OlympiadRankingSerializer, OlympiadHeroSerializer, GrandBossStatusSerializer,
    SiegeSerializer, SiegeParticipantSerializer, BossJewelLocationSerializer,
    CustomTokenObtainPairSerializer, RefreshTokenSerializer, LoginSerializer,
    UserProfileSerializer, ChangePasswordSerializer, CharacterSerializer,
    ItemSerializer, ClanDetailSerializer, AuctionItemSerializer,
    APIResponseSerializer, ServerStatusSerializer
)


class ServerAPISchema:
    """Schema para APIs do servidor Lineage 2"""
    
    @staticmethod
    def players_online_schema():
        return extend_schema(
            summary="Jogadores Online",
            description="Retorna o número de jogadores atualmente online no servidor. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: PlayerOnlineSerializer
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def top_pvp_schema():
        return extend_schema(
            summary="Ranking PvP",
            description="Retorna o ranking dos jogadores com mais PvPs. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def top_pk_schema():
        return extend_schema(
            summary="Ranking PK",
            description="Retorna o ranking dos jogadores com mais PKs. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def top_rich_schema():
        return extend_schema(
            summary="Ranking de Riqueza",
            description="Retorna o ranking dos jogadores mais ricos (Adena). **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def top_online_schema():
        return extend_schema(
            summary="Ranking de Tempo Online",
            description="Retorna o ranking dos jogadores com mais tempo online. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def top_level_schema():
        return extend_schema(
            summary="Ranking de Nível",
            description="Retorna o ranking dos jogadores com maior nível. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10,
                    examples=[
                        OpenApiExample("10 registros", value=10),
                        OpenApiExample("50 registros", value=50),
                        OpenApiExample("100 registros", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: TopPlayerSerializer(many=True)
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def top_clan_schema():
        return extend_schema(
            summary="Ranking de Clãs",
            description="Retorna o ranking dos clãs mais poderosos. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 10, máximo: 100)",
                    default=10
                )
            ],
            responses={
                status.HTTP_200_OK: TopClanSerializer(many=True)
            },
            tags=["Servidor"],
            auth=[]
        )
    
    @staticmethod
    def olympiad_ranking_schema():
        return extend_schema(
            summary="Ranking da Olimpíada",
            description="Retorna o ranking atual da Olimpíada. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: OlympiadRankingSerializer(many=True)
            },
            tags=["Olimpíada"],
            auth=[]
        )
    
    @staticmethod
    def olympiad_heroes_schema(endpoint_name, description):
        return extend_schema(
            summary=f"Heróis da Olimpíada - {endpoint_name}",
            description=f"{description}. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: OlympiadHeroSerializer(many=True)
            },
            tags=["Olimpíada"],
            auth=[]
        )
    
    @staticmethod
    def grandboss_status_schema():
        return extend_schema(
            summary="Status dos Grand Bosses",
            description="Retorna o status atual dos Grand Bosses. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: GrandBossStatusSerializer(many=True)
            },
            tags=["Bosses"],
            auth=[]
        )
    
    @staticmethod
    def siege_schema():
        return extend_schema(
            summary="Status dos Cercos",
            description="Retorna o status atual dos castelos e cercos. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: SiegeSerializer(many=True)
            },
            tags=["Cercos"],
            auth=[]
        )
    
    @staticmethod
    def siege_participants_schema():
        return extend_schema(
            summary="Participantes do Cerco",
            description="Retorna os clãs participantes de um cerco específico. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="castle_id",
                    type=int,
                    location=OpenApiParameter.PATH,
                    description="ID do castelo (1-9)",
                    examples=[
                        OpenApiExample("Castelo Aden", value=1),
                        OpenApiExample("Castelo Dion", value=2),
                        OpenApiExample("Castelo Giran", value=3),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: SiegeParticipantSerializer(many=True)
            },
            tags=["Cercos"],
            auth=[]
        )
    
    @staticmethod
    def boss_jewel_locations_schema():
        return extend_schema(
            summary="Localizações dos Boss Jewels",
            description="Retorna as localizações dos Boss Jewels. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="ids",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    description="IDs dos jewels separados por vírgula",
                    required=True,
                    examples=[
                        OpenApiExample("Jewel 6656", value="6656"),
                        OpenApiExample("Múltiplos jewels", value="6656,6657,6658"),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: BossJewelLocationSerializer(many=True)
            },
            tags=["Bosses"],
            auth=[]
        ) 

# =========================== AUTHENTICATION SCHEMAS ===========================

class AuthAPISchema:
    """Schema para APIs de autenticação"""
    
    @staticmethod
    def login_schema():
        return extend_schema(
            summary="Login de Usuário",
            description="Realiza login do usuário e retorna tokens JWT. **Endpoint público** - não requer autenticação.",
            request=LoginSerializer,
            responses={
                status.HTTP_200_OK: CustomTokenObtainPairSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Autenticação"],
            auth=[]
        )
    
    @staticmethod
    def refresh_token_schema():
        return extend_schema(
            summary="Refresh de Token",
            description="Atualiza o token de acesso usando o refresh token. **Endpoint público** - não requer autenticação.",
            request=RefreshTokenSerializer,
            responses={
                status.HTTP_200_OK: APIResponseSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Autenticação"],
            auth=[]
        )
    
    @staticmethod
    def logout_schema():
        return extend_schema(
            summary="Logout de Usuário 🔒",
            description="Realiza logout do usuário e invalida o refresh token. **Endpoint autenticado** - requer token JWT.",
            responses={
                status.HTTP_200_OK: APIResponseSerializer,
                status.HTTP_400_BAD_REQUEST: APIResponseSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Autenticação"],
            auth=[{'Bearer': []}]
        )


# =========================== USER SCHEMAS ===========================

class UserAPISchema:
    """Schema para APIs de usuário"""
    
    @staticmethod
    def user_profile_schema():
        return extend_schema(
            summary="Perfil do Usuário 🔒",
            description="Retorna ou atualiza o perfil do usuário logado. **Endpoint autenticado** - requer token JWT.",
            responses={
                status.HTTP_200_OK: UserProfileSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Usuário"],
            auth=[{'Bearer': []}]
        )
    
    @staticmethod
    def change_password_schema():
        return extend_schema(
            summary="Alterar Senha 🔒",
            description="Altera a senha do usuário logado. **Endpoint autenticado** - requer token JWT.",
            request=ChangePasswordSerializer,
            responses={
                status.HTTP_200_OK: APIResponseSerializer,
                status.HTTP_400_BAD_REQUEST: APIResponseSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Usuário"],
            auth=[{'Bearer': []}]
        )
    
    @staticmethod
    def user_dashboard_schema():
        return extend_schema(
            summary="Dashboard do Usuário 🔒",
            description="Retorna dados do dashboard do usuário logado. **Endpoint autenticado** - requer token JWT.",
            responses={
                status.HTTP_200_OK: APIResponseSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Usuário"],
            auth=[{'Bearer': []}]
        )
    
    @staticmethod
    def user_stats_schema():
        return extend_schema(
            summary="Estatísticas do Usuário 🔒",
            description="Retorna estatísticas detalhadas do usuário no jogo. **Endpoint autenticado** - requer token JWT.",
            responses={
                status.HTTP_200_OK: APIResponseSerializer,
                status.HTTP_401_UNAUTHORIZED: APIResponseSerializer,
            },
            tags=["Usuário"],
            auth=[{'Bearer': []}]
        )


# =========================== SEARCH SCHEMAS ===========================

class SearchAPISchema:
    """Schema para APIs de busca"""
    
    @staticmethod
    def character_search_schema():
        return extend_schema(
            summary="Busca de Personagens",
            description="Busca personagens no servidor. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="q",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    description="Nome do personagem para buscar (mínimo 2 caracteres)",
                    required=True,
                    examples=[
                        OpenApiExample("Buscar por 'Hero'", value="Hero"),
                        OpenApiExample("Buscar por 'Dark'", value="Dark"),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: CharacterSerializer(many=True),
                status.HTTP_400_BAD_REQUEST: APIResponseSerializer,
            },
            tags=["Busca"],
            auth=[]
        )
    
    @staticmethod
    def item_search_schema():
        return extend_schema(
            summary="Busca de Itens",
            description="Busca itens no servidor. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="q",
                    type=str,
                    location=OpenApiParameter.QUERY,
                    description="Nome do item para buscar (mínimo 2 caracteres)",
                    required=True,
                    examples=[
                        OpenApiExample("Buscar por 'Sword'", value="Sword"),
                        OpenApiExample("Buscar por 'Armor'", value="Armor"),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: ItemSerializer(many=True),
                status.HTTP_400_BAD_REQUEST: APIResponseSerializer,
            },
            tags=["Busca"],
            auth=[]
        )


# =========================== GAME DATA SCHEMAS ===========================

class GameDataAPISchema:
    """Schema para APIs de dados do jogo"""
    
    @staticmethod
    def clan_detail_schema():
        return extend_schema(
            summary="Detalhes do Clã",
            description="Retorna informações detalhadas de um clã específico. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: ClanDetailSerializer,
                status.HTTP_404_NOT_FOUND: APIResponseSerializer,
            },
            tags=["Dados do Jogo"],
            auth=[]
        )
    
    @staticmethod
    def auction_items_schema():
        return extend_schema(
            summary="Itens do Leilão",
            description="Retorna itens disponíveis no leilão. **Endpoint público** - não requer autenticação.",
            parameters=[
                OpenApiParameter(
                    name="limit",
                    type=int,
                    location=OpenApiParameter.QUERY,
                    description="Número máximo de registros (padrão: 20, máximo: 100)",
                    default=20,
                    examples=[
                        OpenApiExample("20 itens", value=20),
                        OpenApiExample("50 itens", value=50),
                        OpenApiExample("100 itens", value=100),
                    ]
                )
            ],
            responses={
                status.HTTP_200_OK: AuctionItemSerializer(many=True),
                status.HTTP_400_BAD_REQUEST: APIResponseSerializer,
            },
            tags=["Dados do Jogo"],
            auth=[]
        )


# =========================== SERVER STATUS SCHEMAS ===========================

class ServerStatusAPISchema:
    """Schema para APIs de status do servidor"""
    
    @staticmethod
    def server_status_schema():
        return extend_schema(
            summary="Status do Servidor",
            description="Retorna o status atual do servidor de jogo. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: ServerStatusSerializer,
            },
            tags=["Status do Servidor"],
            auth=[]
        )


# =========================== API INFO SCHEMAS ===========================

class APIInfoSchema:
    """Schema para informações da API"""
    
    @staticmethod
    def api_info_schema():
        return extend_schema(
            summary="Informações da API",
            description="Retorna informações gerais sobre a API. **Endpoint público** - não requer autenticação.",
            responses={
                status.HTTP_200_OK: APIResponseSerializer,
            },
            tags=["Informações da API"],
            auth=[]
        ) 