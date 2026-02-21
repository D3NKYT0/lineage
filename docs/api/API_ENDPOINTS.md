# 📚 Documentação da API - Lineage 2

> **Última atualização:** 20/02/2026

## 🌐 Base URL
```
http://localhost:80/api/v1/
```

## 🔐 Autenticação

### JWT (JSON Web Tokens)
A API utiliza JWT para autenticação. Para endpoints protegidos, inclua o token no header:
```
Authorization: Bearer <seu_token_aqui>
```

### Tipos de Autenticação
- **Público**: Não requer autenticação
- **Autenticado**: Requer token JWT válido
- **Rate Limited**: Limite de requisições por minuto

---

## 📋 Endpoints Disponíveis

### 🔑 Autenticação

#### POST `/auth/login/`
**Descrição**: Realiza login do usuário e retorna tokens JWT
**Autenticação**: Pública
**Body**:
```json
{
    "username": "seu_usuario",
    "password": "sua_senha"
}
```
**Resposta**:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user_id": 1,
    "username": "seu_usuario",
    "email": "usuario@email.com",
    "first_name": "Nome",
    "last_name": "Sobrenome",
    "is_staff": false,
    "is_superuser": false,
    "message": "Login realizado com sucesso",
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### POST `/auth/refresh/`
**Descrição**: Atualiza o token de acesso usando o refresh token
**Autenticação**: Pública
**Body**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST `/auth/logout/` 🔒
**Descrição**: Realiza logout e invalida o refresh token
**Autenticação**: Autenticado
**Body**:
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

### 👤 Usuário

#### GET `/user/profile/` 🔒
**Descrição**: Retorna o perfil do usuário logado
**Autenticação**: Autenticado
**Resposta**:
```json
{
    "success": true,
    "data": {
        "id": 1,
        "username": "seu_usuario",
        "email": "usuario@email.com",
        "first_name": "Nome",
        "last_name": "Sobrenome",
        "date_joined": "2024-01-01T12:00:00Z",
        "last_login": "2024-01-01T12:00:00Z"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### PUT `/user/profile/` 🔒
**Descrição**: Atualiza o perfil do usuário
**Autenticação**: Autenticado
**Body**:
```json
{
    "first_name": "Novo Nome",
    "last_name": "Novo Sobrenome",
    "email": "novo@email.com"
}
```

#### POST `/user/change-password/` 🔒
**Descrição**: Altera a senha do usuário
**Autenticação**: Autenticado
**Body**:
```json
{
    "old_password": "senha_atual",
    "new_password": "nova_senha",
    "confirm_password": "nova_senha"
}
```

#### GET `/user/dashboard/` 🔒
**Descrição**: Retorna dados do dashboard do usuário
**Autenticação**: Autenticado
**Resposta**:
```json
{
    "success": true,
    "data": {
        "user_info": {
            "username": "seu_usuario",
            "email": "usuario@email.com",
            "date_joined": "2024-01-01T12:00:00Z",
            "last_login": "2024-01-01T12:00:00Z"
        },
        "game_stats": {
            "characters": 3,
            "total_level": 150,
            "total_online_time": 7200
        },
        "server_status": {
            "online": true,
            "players_online": 150
        }
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET `/user/stats/` 🔒
**Descrição**: Retorna estatísticas detalhadas do usuário no jogo
**Autenticação**: Autenticado

---

### 🖥️ Status do Servidor

#### GET `/server/status/`
**Descrição**: Retorna o status atual do servidor
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Resposta**:
```json
{
    "success": true,
    "data": {
        "server_name": "Lineage 2 Server",
        "status": "online",
        "players_online": 150,
        "max_players": 1000,
        "uptime": "24h 30m",
        "last_update": "2024-01-01T12:00:00Z",
        "version": "1.9.0",
        "maintenance_mode": false
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET `/server/players-online/`
**Descrição**: Retorna o número de jogadores online
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Resposta**:
```json
{
    "online_count": 150,
    "fake_players": 0,
    "real_players": 150
}
```

---

### 🏆 Rankings

#### GET `/server/top-pvp/`
**Descrição**: Ranking dos jogadores com mais PvPs
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Parâmetros**:
- `limit` (opcional): Número de registros (padrão: 10, máximo: 100)

#### GET `/server/top-pk/`
**Descrição**: Ranking dos jogadores com mais PKs
**Autenticação**: Pública
**Rate Limit**: 30/minuto

#### GET `/server/top-clan/`
**Descrição**: Ranking dos clãs mais poderosos
**Autenticação**: Pública
**Rate Limit**: 30/minuto

#### GET `/server/top-rich/`
**Descrição**: Ranking dos jogadores mais ricos (Adena)
**Autenticação**: Pública
**Rate Limit**: 30/minuto

#### GET `/server/top-online/`
**Descrição**: Ranking dos jogadores com mais tempo online
**Autenticação**: Pública
**Rate Limit**: 30/minuto

#### GET `/server/top-level/`
**Descrição**: Ranking dos jogadores com maior nível
**Autenticação**: Pública
**Rate Limit**: 30/minuto

---

### 🏅 Olimpíada

#### GET `/server/olympiad-ranking/`
**Descrição**: Ranking atual da Olimpíada
**Autenticação**: Pública
**Rate Limit**: 30/minuto

#### GET `/server/olympiad-heroes/`
**Descrição**: Todos os heróis da Olimpíada
**Autenticação**: Pública
**Rate Limit**: 30/minuto

#### GET `/server/olympiad-current-heroes/`
**Descrição**: Heróis atuais da Olimpíada
**Autenticação**: Pública
**Rate Limit**: 30/minuto

---

### 🐉 Bosses

#### GET `/server/grandboss-status/`
**Descrição**: Status dos Grand Bosses
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Resposta**:
```json
[
    {
        "boss_name": "Antharas",
        "boss_id": 29019,
        "is_alive": false,
        "respawn_time": "2024-01-01T18:00:00Z",
        "location": "Antharas Lair"
    }
]
```

#### GET `/server/boss-jewel-locations/`
**Descrição**: Localizações dos Boss Jewels
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Parâmetros**:
- `ids` (obrigatório): IDs dos jewels separados por vírgula (ex: 6656,6657,6658)

---

### 🏰 Cercos

#### GET `/server/siege/`
**Descrição**: Status dos cercos
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Resposta**:
```json
[
    {
        "castle_name": "Aden Castle",
        "castle_id": 1,
        "owner_clan": "ClanName",
        "siege_date": "2024-01-01T20:00:00Z",
        "is_under_siege": false
    }
]
```

#### GET `/server/siege-participants/{castle_id}/`
**Descrição**: Participantes de um cerco específico
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Parâmetros**:
- `castle_id`: ID do castelo (1-9)

---

### 🔍 Busca

#### GET `/search/character/`
**Descrição**: Busca personagens no servidor
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Parâmetros**:
- `q` (obrigatório): Nome do personagem (mínimo 2 caracteres)
**Resposta**:
```json
{
    "success": true,
    "data": [
        {
            "char_id": 1,
            "char_name": "HeroName",
            "level": 85,
            "class_name": "Warlord",
            "clan_name": "ClanName",
            "online": true,
            "last_access": "2024-01-01T12:00:00Z",
            "x": 1000,
            "y": 1000,
            "z": -100
        }
    ],
    "count": 1,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET `/search/item/`
**Descrição**: Busca itens no servidor
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Parâmetros**:
- `q` (obrigatório): Nome do item (mínimo 2 caracteres)

---

### 🎮 Dados do Jogo

#### GET `/clan/{clan_name}/`
**Descrição**: Detalhes de um clã específico
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Resposta**:
```json
{
    "success": true,
    "data": {
        "clan_id": 1,
        "clan_name": "ClanName",
        "leader_name": "LeaderName",
        "level": 5,
        "member_count": 50,
        "reputation": 1000,
        "ally_name": "AllyName",
        "creation_date": "2024-01-01T12:00:00Z",
        "description": "Clan description"
    },
    "timestamp": "2024-01-01T12:00:00Z"
}
```

#### GET `/auction/items/`
**Descrição**: Itens disponíveis no leilão
**Autenticação**: Pública
**Rate Limit**: 30/minuto
**Parâmetros**:
- `limit` (opcional): Número de itens (padrão: 20, máximo: 100)
**Resposta**:
```json
{
    "success": true,
    "data": [
        {
            "auction_id": 1,
            "item_name": "Sword of Valakas",
            "seller_name": "SellerName",
            "current_bid": 1000000,
            "min_bid": 1100000,
            "end_time": "2024-01-01T18:00:00Z",
            "item_count": 1,
            "item_grade": "S",
            "item_enchant": 0
        }
    ],
    "count": 1,
    "timestamp": "2024-01-01T12:00:00Z"
}
```

---

## 📊 Rate Limits

- **Usuários Anônimos**: 30 requisições por minuto
- **Usuários Autenticados**: 100 requisições por minuto

## 🔧 Códigos de Status HTTP

- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Não autorizado
- `404 Not Found`: Recurso não encontrado
- `429 Too Many Requests`: Rate limit excedido
- `500 Internal Server Error`: Erro interno do servidor

## 📖 Documentação Interativa

Acesse a documentação interativa da API:
- **Swagger UI**: `/api/v1/schema/swagger/`
- **ReDoc**: `/api/v1/schema/redoc/`
- **Schema OpenAPI**: `/api/v1/schema/`

## 🚀 Exemplos de Uso

### Login e Autenticação
```bash
# Login
curl -X POST http://localhost:80/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "seu_usuario", "password": "sua_senha"}'

# Usar token em requisições
curl -H "Authorization: Bearer <seu_token>" \
  http://localhost:80/api/v1/user/profile/
```

### Buscar Personagens
```bash
curl "http://localhost:80/api/v1/search/character/?q=Hero"
```

### Status do Servidor
```bash
curl http://localhost:80/api/v1/server/status/
```

### Ranking PvP
```bash
curl "http://localhost:80/api/v1/server/top-pvp/?limit=10"
```

---

## 🔄 Versão da API

- **Versão Atual**: 1.0.0
- **Base URL**: `/api/v1/`
- **Formato**: JSON
- **Encoding**: UTF-8

## 📋 Resumo dos Endpoints

### 🔓 Endpoints Públicos (Sem Autenticação)
- `POST /auth/login/` - Login
- `POST /auth/refresh/` - Refresh token
- `GET /server/status/` - Status do servidor
- `GET /server/players-online/` - Jogadores online
- `GET /server/top-pvp/` - Ranking PvP
- `GET /server/top-pk/` - Ranking PK
- `GET /server/top-clan/` - Ranking de clãs
- `GET /server/top-rich/` - Ranking de riqueza
- `GET /server/top-online/` - Ranking de tempo online
- `GET /server/top-level/` - Ranking de nível
- `GET /server/olympiad-ranking/` - Ranking da Olimpíada
- `GET /server/olympiad-heroes/` - Todos os heróis da Olimpíada
- `GET /server/olympiad-current-heroes/` - Heróis atuais da Olimpíada
- `GET /server/grandboss-status/` - Status dos Grand Bosses
- `GET /server/siege/` - Status dos cercos
- `GET /server/siege-participants/{id}/` - Participantes do cerco
- `GET /server/boss-jewel-locations/` - Localizações dos Boss Jewels
- `GET /search/character/` - Busca de personagens
- `GET /search/item/` - Busca de itens
- `GET /clan/{nome}/` - Detalhes do clã
- `GET /auction/items/` - Itens do leilão

### 🔒 Endpoints Autenticados (Requerem Token JWT)
- `POST /auth/logout/` - Logout
- `GET /user/profile/` - Perfil do usuário
- `PUT /user/profile/` - Atualizar perfil
- `POST /user/change-password/` - Alterar senha
- `GET /user/dashboard/` - Dashboard do usuário
- `GET /user/stats/` - Estatísticas do usuário

## 📞 Suporte

Para dúvidas ou problemas com a API:
- **Documentação**: `/api/v1/schema/swagger/`
- **Issues**: Abra uma issue no repositório
- **Email**: suporte@seudominio.com 