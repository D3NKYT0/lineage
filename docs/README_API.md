# API App - Lineage 2 L2JPremium

Este app fornece APIs públicas para o servidor Lineage 2 usando Django REST Framework (DRF).

## Estrutura

```
apps/api/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── serializers.py      # Serializers para validação de dados
├── schema.py          # Configuração de documentação da API
├── tests.py
├── urls.py            # URLs da API
├── views.py           # Views da API
└── README.md          # Este arquivo
```

## Endpoints Disponíveis

### 🔓 Endpoints Públicos (Sem Autenticação)

#### Servidor
- `GET /api/server/players-online/` - Jogadores online
- `GET /api/server/top-pvp/` - Ranking PvP
- `GET /api/server/top-pk/` - Ranking PK
- `GET /api/server/top-clan/` - Ranking de clãs
- `GET /api/server/top-rich/` - Ranking de riqueza
- `GET /api/server/top-online/` - Ranking de tempo online
- `GET /api/server/top-level/` - Ranking de nível

#### Olimpíada
- `GET /api/server/olympiad-ranking/` - Ranking da Olimpíada
- `GET /api/server/olympiad-heroes/` - Todos os heróis
- `GET /api/server/olympiad-current-heroes/` - Heróis atuais

#### Bosses
- `GET /api/server/grandboss-status/` - Status dos Grand Bosses
- `GET /api/server/boss-jewel-locations/` - Localizações dos Boss Jewels

#### Cercos
- `GET /api/server/siege/` - Status dos cercos
- `GET /api/server/siege-participants/{castle_id}/` - Participantes do cerco

#### Busca e Dados do Jogo
- `GET /api/search/character/` - Busca de personagens
- `GET /api/search/item/` - Busca de itens
- `GET /api/clan/{nome}/` - Detalhes do clã
- `GET /api/auction/items/` - Itens do leilão

#### Autenticação (Pública para obter tokens)
- `POST /api/auth/login/` - Login
- `POST /api/auth/refresh/` - Refresh token

### 🔒 Endpoints Autenticados (Requerem Token JWT)

#### Usuário
- `POST /api/auth/logout/` - Logout
- `GET /api/user/profile/` - Perfil do usuário
- `PUT /api/user/profile/` - Atualizar perfil
- `POST /api/user/change-password/` - Alterar senha
- `GET /api/user/dashboard/` - Dashboard do usuário
- `GET /api/user/stats/` - Estatísticas do usuário

## Características

### Autenticação
- **JWT (JSON Web Tokens)**: Para endpoints protegidos
- **Endpoints Públicos**: Não requerem autenticação
- **Endpoints Autenticados**: Requerem token JWT no header `Authorization: Bearer <token>`

### Rate Limiting
- **APIs Públicas**: 30 requisições por minuto por IP
- **APIs de Usuário**: 100 requisições por minuto por usuário autenticado

### Cache
- **Jogadores Online**: 30 segundos
- **Rankings**: 1 minuto
- **Olimpíada**: 5 minutos
- **Bosses**: 1 minuto
- **Cercos**: 5 minutos

### Documentação
- Documentação automática com DRF Spectacular
- Swagger UI disponível em `/api/v1/schema/swagger/`
- OpenAPI 3.0 schema em `/api/v1/schema/`

### Validação
- Serializers para validação de entrada e saída
- Validação de parâmetros (limit, castle_id, jewel_ids)
- Tratamento de erros padronizado

## Configuração

### Dependências
- `djangorestframework`
- `drf-spectacular`

### Settings
O app está configurado em `core/settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_spectacular',
    'apps.api',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '30/minute',
        'user': '100/minute'
    }
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Lineage 2 L2JPremium API',
    'DESCRIPTION': 'API pública para servidores privados de Lineage 2',
    'VERSION': '1.0.0',
    # ...
}
```

### URLs
As URLs estão configuradas em `core/urls.py`:

```python
urlpatterns = [
    # ...
    path('', include('apps.api.urls')),
    path('api/schema/', include('drf_spectacular.urls')),
    # ...
]
```

## Uso

### Endpoints Públicos
```bash
# Jogadores online
curl -X GET "https://seu-dominio.com/api/server/players-online/"

# Ranking PvP com limite
curl -X GET "https://seu-dominio.com/api/server/top-pvp/?limit=10"
```

### Endpoints Autenticados
```bash
# Login para obter token
curl -X POST "https://seu-dominio.com/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_usuario", "password": "sua_senha"}'

# Usar token para acessar perfil
curl -X GET "https://seu-dominio.com/api/user/profile/" \
  -H "Authorization: Bearer <seu_token_aqui>"
```

### Exemplo de Resposta (Público)
```json
{
    "online_count": 150,
    "fake_players": 10,
    "real_players": 140
}
```

### Exemplo de Resposta (Autenticado)
```json
{
    "username": "seu_usuario",
    "email": "usuario@exemplo.com",
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
}
```

## Testes

Execute os testes com:

```bash
python manage.py test apps.api
```

Ou execute os testes manuais:

```bash
python test/test_drf_api.py
```

## Desenvolvimento

### Adicionando Novos Endpoints

1. **Criar o Serializer** em `serializers.py`
2. **Criar a View** em `views.py`
3. **Adicionar a URL** em `urls.py`
4. **Adicionar o Schema** em `schema.py`
5. **Criar testes** em `tests.py`

### Exemplo de Novo Endpoint

```python
# serializers.py
class NewDataSerializer(serializers.Serializer):
    field1 = serializers.CharField()
    field2 = serializers.IntegerField()

# views.py
@api_view(['GET'])
@throttle_classes([PublicAPIRateThrottle])
@endpoint_enabled('new_endpoint')
@ServerAPISchema.new_endpoint_schema()
def new_endpoint(request):
    # Lógica da view
    data = LineageStats.new_data()
    serializer = NewDataSerializer(data, many=True)
    return Response(serializer.data)

# urls.py
path('server/new-endpoint/', views.new_endpoint, name='new_endpoint'),

# schema.py
@staticmethod
def new_endpoint_schema():
    return extend_schema(
        summary="Novo Endpoint",
        description="Descrição do novo endpoint",
        responses={status.HTTP_200_OK: NewDataSerializer},
        tags=["Servidor"]
    )
```

## Monitoramento

### Logs
As APIs geram logs para monitoramento:
- Requisições bem-sucedidas
- Erros de validação
- Rate limiting excedido
- Erros de servidor

### Métricas
- Número de requisições por endpoint
- Tempo de resposta
- Taxa de erro
- Uso de cache

## Segurança

- Rate limiting para prevenir abuso
- Validação de entrada
- Sanitização de dados
- Headers de segurança
- CORS configurado

## Suporte

Para dúvidas ou problemas:
1. Verifique a documentação em `/api/schema/swagger-ui/`
2. Consulte os logs do servidor
3. Execute os testes para verificar a funcionalidade
4. Entre em contato com a equipe de desenvolvimento 