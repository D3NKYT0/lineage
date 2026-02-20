# Documentação da API REST

## Autenticação
- A maioria dos endpoints da API utiliza **JWT (JSON Web Tokens)**
- Endpoints públicos: jogadores online, rankings, bosses, etc.
- Endpoints autenticados: perfil, dashboard, logout, etc.

### Header de autenticação
```http
Authorization: Bearer <seu_token_aqui>
```

### Obter token
Faça login em `POST /api/auth/login/` com username e password para obter os tokens.

---

## Principais Endpoints

### Exemplo: Ranking de Jogadores
- `GET /api/server/top-level/?limit=10`
- **Resposta:**
  ```json
  [
    {"char_name": "Hero", "level": 80, "clan_name": "Lendas", ...},
    ...
  ]
  ```

### Exemplo: Status dos Cercos
- `GET /api/server/siege/`
- **Resposta:**
  ```json
  [
    {"castle": "Aden", "owner": "ClanX", "siege_date": "2024-06-01"},
    ...
  ]
  ```

### Exemplo: Jogadores Online
- `GET /api/server/players-online/`
- **Resposta:**
  ```json
  {
    "online_count": 150,
    "fake_players": 10,
    "real_players": 140
  }
  ```

---

## Formato de Erros
As respostas de erro seguem o padrão:
```json
{
  "error": "Mensagem de erro",
  "detail": "Detalhes adicionais (quando aplicável)"
}
```

---

## Documentação Completa
- **Swagger UI:** `/api/schema/swagger-ui/` ou `/api/v1/schema/swagger/`
- **OpenAPI:** `/api/schema/` ou `/api/v1/schema/`
- Documentação detalhada em [API_DOCUMENTATION.md](API_DOCUMENTATION.md) e [API_ENDPOINTS.md](API_ENDPOINTS.md)

## Código de Referência
Consulte `apps/api/` para views, serializers e URLs da API.
