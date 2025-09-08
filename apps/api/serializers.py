from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from apps.main.home.models import User as CustomUser


class PlayerOnlineSerializer(serializers.Serializer):
    """Serializer para dados de jogadores online"""
    online_count = serializers.IntegerField()
    fake_players = serializers.IntegerField(required=False)
    real_players = serializers.IntegerField(required=False)


class TopPlayerSerializer(serializers.Serializer):
    """Serializer para dados de ranking de jogadores"""
    char_name = serializers.CharField()
    level = serializers.IntegerField()
    clan_name = serializers.CharField(allow_blank=True, allow_null=True)
    pvp_count = serializers.IntegerField(required=False)
    pk_count = serializers.IntegerField(required=False)
    adena = serializers.IntegerField(required=False)
    online_time = serializers.IntegerField(required=False)
    class_name = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class TopClanSerializer(serializers.Serializer):
    """Serializer para dados de ranking de clãs"""
    clan_name = serializers.CharField()
    leader_name = serializers.CharField()
    level = serializers.IntegerField()
    member_count = serializers.IntegerField()
    reputation = serializers.IntegerField(required=False)


class OlympiadRankingSerializer(serializers.Serializer):
    """Serializer para dados de ranking da Olimpíada"""
    char_name = serializers.CharField()
    class_name = serializers.CharField()
    points = serializers.IntegerField()
    rank = serializers.IntegerField()


class OlympiadHeroSerializer(serializers.Serializer):
    """Serializer para dados de heróis da Olimpíada"""
    char_name = serializers.CharField()
    class_name = serializers.CharField()
    hero_type = serializers.CharField()
    hero_count = serializers.IntegerField()
    hero_date = serializers.DateField(required=False, allow_null=True)


class GrandBossStatusSerializer(serializers.Serializer):
    """Serializer para status dos Grand Bosses"""
    boss_name = serializers.CharField()
    boss_id = serializers.IntegerField()
    is_alive = serializers.BooleanField()
    respawn_time = serializers.DateTimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True)


class SiegeSerializer(serializers.Serializer):
    """Serializer para dados de cerco"""
    castle_name = serializers.CharField()
    castle_id = serializers.IntegerField()
    owner_clan = serializers.CharField(allow_blank=True, allow_null=True)
    siege_date = serializers.DateTimeField(required=False, allow_null=True)
    is_under_siege = serializers.BooleanField()


class SiegeParticipantSerializer(serializers.Serializer):
    """Serializer para participantes do cerco"""
    clan_name = serializers.CharField()
    leader_name = serializers.CharField()
    member_count = serializers.IntegerField()
    registration_date = serializers.DateTimeField(required=False, allow_null=True)


class BossJewelLocationSerializer(serializers.Serializer):
    """Serializer para localizações dos Boss Jewels"""
    jewel_id = serializers.IntegerField()
    jewel_name = serializers.CharField()
    location = serializers.CharField()
    coordinates = serializers.CharField(required=False, allow_blank=True)
    respawn_time = serializers.DateTimeField(required=False, allow_null=True)


# =========================== AUTHENTICATION SERIALIZERS ===========================

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Serializer customizado para login JWT"""
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Adiciona informações extras do usuário
        user = self.user
        data.update({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })
        
        return data


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer para refresh de token"""
    refresh = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    """Serializer para login"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Credenciais inválidas.')
            if not user.is_active:
                raise serializers.ValidationError('Usuário desativado.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Username e password são obrigatórios.')
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para perfil do usuário"""
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para mudança de senha"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("As senhas não coincidem.")
        return attrs


# =========================== GAME SERIALIZERS ===========================

class CharacterSerializer(serializers.Serializer):
    """Serializer para personagens do jogo"""
    char_id = serializers.IntegerField()
    char_name = serializers.CharField()
    level = serializers.IntegerField()
    class_name = serializers.CharField()
    clan_name = serializers.CharField(allow_blank=True, allow_null=True)
    online = serializers.BooleanField()
    last_access = serializers.DateTimeField(required=False, allow_null=True)
    x = serializers.IntegerField(required=False)
    y = serializers.IntegerField(required=False)
    z = serializers.IntegerField(required=False)


class ItemSerializer(serializers.Serializer):
    """Serializer para itens do jogo"""
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    item_type = serializers.CharField()
    grade = serializers.CharField(required=False)
    enchant_level = serializers.IntegerField(required=False)
    price = serializers.IntegerField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class ClanDetailSerializer(serializers.Serializer):
    """Serializer para detalhes de clã"""
    clan_id = serializers.IntegerField()
    clan_name = serializers.CharField()
    leader_name = serializers.CharField()
    level = serializers.IntegerField()
    member_count = serializers.IntegerField()
    reputation = serializers.IntegerField()
    ally_name = serializers.CharField(allow_blank=True, allow_null=True)
    creation_date = serializers.DateTimeField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)


class AuctionItemSerializer(serializers.Serializer):
    """Serializer para itens do leilão"""
    auction_id = serializers.IntegerField()
    item_name = serializers.CharField()
    seller_name = serializers.CharField()
    current_bid = serializers.IntegerField()
    min_bid = serializers.IntegerField()
    end_time = serializers.DateTimeField()
    item_count = serializers.IntegerField()
    item_grade = serializers.CharField(required=False)
    item_enchant = serializers.IntegerField(required=False)


# =========================== RESPONSE SERIALIZERS ===========================

class APIResponseSerializer(serializers.Serializer):
    """Serializer padrão para respostas da API"""
    success = serializers.BooleanField()
    message = serializers.CharField(required=False, allow_blank=True)
    data = serializers.JSONField(required=False)
    errors = serializers.ListField(child=serializers.CharField(), required=False)
    timestamp = serializers.DateTimeField()
    version = serializers.CharField()


class PaginationSerializer(serializers.Serializer):
    """Serializer para informações de paginação"""
    count = serializers.IntegerField()
    next = serializers.CharField(allow_null=True, allow_blank=True)
    previous = serializers.CharField(allow_null=True, allow_blank=True)
    results = serializers.ListField()


class ServerStatusSerializer(serializers.Serializer):
    """Serializer para status do servidor"""
    server_name = serializers.CharField()
    status = serializers.CharField()  # online, offline, maintenance
    players_online = serializers.IntegerField()
    max_players = serializers.IntegerField()
    uptime = serializers.CharField(required=False)
    last_update = serializers.DateTimeField()
    version = serializers.CharField(required=False)
    maintenance_mode = serializers.BooleanField(default=False) 