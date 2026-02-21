# API Documentation - Lineage 2 PDL

> **Última atualização:** 20/02/2026

## Visão Geral

Esta API fornece acesso aos dados do servidor Lineage 2, incluindo rankings, status de bosses, informações da Olimpíada e muito mais. A maioria dos endpoints é pública, mas alguns requerem autenticação.

## Base URL

```
https://seu-dominio.com/api/
```

## Autenticação

### Endpoints Públicos
A maioria dos endpoints não requer autenticação, mas possuem rate limiting para proteger contra abuso.

### Endpoints Autenticados
Alguns endpoints requerem autenticação JWT. Para usar estes endpoints:

1. Faça login em `/api/auth/login/` para obter um token de acesso
2. Inclua o token no header: `Authorization: Bearer <seu_token>`
3. Use `/api/auth/refresh/` para renovar o token quando necessário

## Rate Limiting

- **APIs Públicas**: 30 requisições por minuto por IP
- **APIs de Usuário**: 100 requisições por minuto por usuário autenticado

## Endpoints

### Autenticação

#### Login
```http
POST /api/auth/login/
```

**Corpo da requisição:**
```json
{
    "username": "seu_usuario",
    "password": "sua_senha"
}
```

**Resposta:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token
```http
POST /api/auth/refresh/
```

**Corpo da requisição:**
```json
{
    "refresh": "seu_refresh_token"
}
```

#### Logout 🔒
```http
POST /api/auth/logout/
```

**Headers:**
```
Authorization: Bearer <seu_token>
```

### Usuário (Autenticado)

#### Perfil do Usuário 🔒
```http
GET /api/user/profile/
```

**Headers:**
```
Authorization: Bearer <seu_token>
```

**Resposta:**
```json
{
    "username": "seu_usuario",
    "email": "usuario@exemplo.com",
    "date_joined": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
}
```

#### Atualizar Perfil 🔒
```http
PUT /api/user/profile/
```

**Headers:**
```
Authorization: Bearer <seu_token>
```

#### Alterar Senha 🔒
```http
POST /api/user/change-password/
```

**Headers:**
```
Authorization: Bearer <seu_token>
```

**Corpo da requisição:**
```json
{
    "old_password": "senha_atual",
    "new_password": "nova_senha"
}
```

#### Dashboard do Usuário 🔒
```http
GET /api/user/dashboard/
```

**Headers:**
```
Authorization: Bearer <seu_token>
```

#### Estatísticas do Usuário 🔒
```http
GET /api/user/stats/
```

**Headers:**
```
Authorization: Bearer <seu_token>
```

### Servidor

#### Jogadores Online
```http
GET /api/server/players-online/
```

**Resposta:**
```json
{
    "online_count": 150,
    "fake_players": 10,
    "real_players": 140
}
```

#### Ranking PvP
```http
GET /api/server/top-pvp/?limit=10
```

**Parâmetros:**
- `limit` (opcional): Número de registros (padrão: 10, máximo: 100)

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "level": 80,
        "clan_name": "Lendas",
        "class_name": "Warlord",
        "pvp_count": 1500
    }
]
```

#### Ranking PK
```http
GET /api/server/top-pk/?limit=10
```

**Parâmetros:**
- `limit` (opcional): Número de registros (padrão: 10, máximo: 100)

#### Ranking de Clãs
```http
GET /api/server/top-clan/?limit=10
```

**Resposta:**
```json
[
    {
        "clan_name": "Lendas",
        "leader_name": "HeroPlayer",
        "level": 5,
        "member_count": 50,
        "reputation": 10000
    }
]
```

#### Ranking de Riqueza (Adena)
```http
GET /api/server/top-rich/?limit=10
```

#### Ranking de Tempo Online
```http
GET /api/server/top-online/?limit=10
```

#### Ranking de Nível
```http
GET /api/server/top-level/?limit=10
```

### Olimpíada

#### Ranking da Olimpíada
```http
GET /api/server/olympiad-ranking/
```

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "class_name": "Warlord",
        "points": 2500,
        "rank": 1
    }
]
```

#### Todos os Heróis da Olimpíada
```http
GET /api/server/olympiad-heroes/
```

#### Heróis Atuais da Olimpíada
```http
GET /api/server/olympiad-current-heroes/
```

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "class_name": "Warlord",
        "hero_type": "current",
        "hero_count": 3,
        "hero_date": "2024-01-15"
    }
]
```

### Bosses

#### Status dos Grand Bosses
```http
GET /api/server/grandboss-status/
```

**Resposta:**
```json
[
    {
        "boss_name": "Antharas",
        "boss_id": 29019,
        "is_alive": false,
        "respawn_time": "2024-01-16T10:00:00Z",
        "location": "Antharas Lair"
    }
]
```

#### Localizações dos Boss Jewels
```http
GET /api/server/boss-jewel-locations/?ids=6656,6657,6658
```

**Parâmetros:**
- `ids` (obrigatório): IDs dos jewels separados por vírgula

**IDs Válidos:** 6656, 6657, 6658, 6659, 6660, 6661, 6662, 8191, 16025, 16026, 21712, 22173, 22174, 22175

**Resposta:**
```json
[
    {
        "jewel_id": 6656,
        "jewel_name": "Antharas Jewel",
        "location": "Antharas Lair",
        "coordinates": "131983, 114509, -3718",
        "respawn_time": "2024-01-16T10:00:00Z"
    }
]
```

### Cercos

#### Status dos Cercos
```http
GET /api/server/siege/
```

**Resposta:**
```json
[
    {
        "castle_name": "Aden",
        "castle_id": 1,
        "owner_clan": "Lendas",
        "siege_date": "2024-01-20T20:00:00Z",
        "is_under_siege": false
    }
]
```

#### Participantes do Cerco
```http
GET /api/server/siege-participants/1/
```

**Parâmetros:**
- `castle_id` (path): ID do castelo (1-9)

**Resposta:**
```json
[
    {
        "clan_name": "Lendas",
        "leader_name": "HeroPlayer",
        "member_count": 50,
        "registration_date": "2024-01-15T10:00:00Z"
    }
]
```

### Busca

#### Buscar Personagem
```http
GET /api/search/character/?name=HeroPlayer
```

**Parâmetros:**
- `name` (obrigatório): Nome do personagem

**Resposta:**
```json
[
    {
        "char_name": "HeroPlayer",
        "level": 80,
        "class_name": "Warlord",
        "clan_name": "Lendas",
        "online": true
    }
]
```

#### Buscar Item
```http
GET /api/search/item/?name=sword
```

**Parâmetros:**
- `name` (obrigatório): Nome do item

**Resposta:**
```json
[
    {
        "item_id": 1234,
        "item_name": "Sword of Light",
        "grade": "A",
        "type": "weapon"
    }
]
```

### Dados do Jogo

#### Detalhes do Clã
```http
GET /api/clan/Lendas/
```

**Parâmetros:**
- `clan_name` (path): Nome do clã

**Resposta:**
```json
{
    "clan_name": "Lendas",
    "leader_name": "HeroPlayer",
    "level": 5,
    "member_count": 50,
    "reputation": 10000,
    "description": "Clã dos lendários"
}
```

#### Itens do Leilão
```http
GET /api/auction/items/?limit=10
```

**Parâmetros:**
- `limit` (opcional): Número de itens (padrão: 10, máximo: 100)

**Resposta:**
```json
[
    {
        "item_id": 1234,
        "item_name": "Sword of Light",
        "seller": "HeroPlayer",
        "current_bid": 1000000,
        "end_time": "2024-01-20T20:00:00Z"
    }
]
```

## Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `400 Bad Request`: Parâmetros inválidos
- `404 Not Found`: Endpoint não encontrado
- `429 Too Many Requests`: Rate limit excedido
- `500 Internal Server Error`: Erro interno do servidor

## Exemplos de Uso

### JavaScript (Fetch)
```javascript
// Endpoints públicos
// Buscar jogadores online
fetch('/api/server/players-online/')
    .then(response => response.json())
    .then(data => console.log(data));

// Buscar top 10 PvP
fetch('/api/server/top-pvp/?limit=10')
    .then(response => response.json())
    .then(data => console.log(data));

// Endpoints autenticados
// Login
fetch('/api/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        username: 'seu_usuario',
        password: 'sua_senha'
    })
})
.then(response => response.json())
.then(data => {
    const token = data.access;
    
    // Usar o token para acessar endpoints autenticados
    fetch('/api/user/profile/', {
        headers: {
            'Authorization': `Bearer ${token}`
        }
    })
    .then(response => response.json())
    .then(profile => console.log(profile));
});
```

### Python (Requests)
```python
import requests

# Endpoints públicos
# Buscar jogadores online
response = requests.get('https://seu-dominio.com/api/server/players-online/')
data = response.json()
print(data)

# Buscar top 10 PvP
response = requests.get('https://seu-dominio.com/api/server/top-pvp/', params={'limit': 10})
data = response.json()
print(data)

# Endpoints autenticados
# Login
login_data = {
    'username': 'seu_usuario',
    'password': 'sua_senha'
}
response = requests.post('https://seu-dominio.com/api/auth/login/', json=login_data)
tokens = response.json()
access_token = tokens['access']

# Usar o token para acessar endpoints autenticados
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get('https://seu-dominio.com/api/user/profile/', headers=headers)
profile = response.json()
print(profile)
```

### cURL
```bash
# Endpoints públicos
# Jogadores online
curl -X GET "https://seu-dominio.com/api/server/players-online/"

# Top 10 PvP
curl -X GET "https://seu-dominio.com/api/server/top-pvp/?limit=10"

# Endpoints autenticados
# Login
curl -X POST "https://seu-dominio.com/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_usuario", "password": "sua_senha"}'

# Usar o token para acessar perfil
curl -X GET "https://seu-dominio.com/api/user/profile/" \
  -H "Authorization: Bearer seu_token_aqui"
```

## Resumo dos Endpoints

### Endpoints Públicos (Sem Autenticação)
- `GET /api/server/status/` - Status do servidor
- `GET /api/server/players-online/` - Jogadores online
- `GET /api/server/top-pvp/` - Ranking PvP
- `GET /api/server/top-pk/` - Ranking PK
- `GET /api/server/top-clan/` - Ranking de clãs
- `GET /api/server/top-rich/` - Ranking de riqueza
- `GET /api/server/top-online/` - Ranking de tempo online
- `GET /api/server/top-level/` - Ranking de nível
- `GET /api/server/olympiad-ranking/` - Ranking da Olimpíada
- `GET /api/server/olympiad-heroes/` - Todos os heróis da Olimpíada
- `GET /api/server/olympiad-current-heroes/` - Heróis atuais da Olimpíada
- `GET /api/server/grandboss-status/` - Status dos Grand Bosses
- `GET /api/server/siege/` - Status dos cercos
- `GET /api/server/siege-participants/<id>/` - Participantes do cerco
- `GET /api/server/boss-jewel-locations/` - Localizações dos Boss Jewels
- `GET /api/search/character/` - Busca de personagens
- `GET /api/search/item/` - Busca de itens
- `GET /api/clan/<nome>/` - Detalhes do clã
- `GET /api/auction/items/` - Itens do leilão
- `POST /api/auth/login/` - Login (para obter token)
- `POST /api/auth/refresh/` - Refresh token

### Endpoints Autenticados (Requerem Token JWT) 🔒
- `POST /api/auth/logout/` - Logout
- `GET /api/user/profile/` - Perfil do usuário
- `PUT /api/user/profile/` - Atualizar perfil
- `POST /api/user/change-password/` - Alterar senha
- `GET /api/user/dashboard/` - Dashboard do usuário
- `GET /api/user/stats/` - Estatísticas do usuário

## Cache

As APIs utilizam cache para melhorar a performance:
- **Jogadores Online**: 30 segundos
- **Rankings**: 1 minuto
- **Olimpíada**: 5 minutos
- **Bosses**: 1 minuto
- **Cercos**: 5 minutos

## Documentação Interativa

Acesse a documentação interativa da API em:
```
https://seu-dominio.com/api/v1/schema/swagger/
```

## Suporte

Para suporte técnico ou dúvidas sobre a API, entre em contato através do Discord ou email do servidor. 