# API v1 — Uso no app PWA

## Já utilizados no app

| Endpoint | Onde |
|----------|------|
| `POST /api/v1/auth/login/` | App.js (login) |
| `GET /api/v1/user/profile/` | UserSection |
| `GET /api/v1/user/dashboard/` | UserSection |
| `GET /api/v1/user/stats/` | UserSection |
| `POST /api/v1/user/change-password/` | UserSection |
| `GET /api/v1/server/status/` | UserSection, ServerSection |
| `GET /api/v1/server/top-level/` | ServerSection |
| `GET /api/v1/server/top-pvp/` | ServerSection |
| `GET /api/v1/server/top-pk/` | ServerSection |
| `GET /api/v1/server/top-rich/` | ServerSection |
| `GET /api/v1/server/top-online/` | ServerSection |
| `GET /api/v1/server/top-clan/` | ServerSection |
| `GET /api/v1/server/olympiad-ranking/` | ServerSection |
| `GET /api/v1/server/olympiad-heroes/` | ServerSection |
| `GET /api/v1/server/grandboss-status/` | ServerSection |
| `GET /api/v1/server/siege/` | ServerSection |
| `GET /api/v1/search/character/?q=` | SearchSection |
| `GET /api/v1/search/item/?q=` | SearchSection |
| `GET /api/v1/clan/{name}/` | GameSection |
| `GET /api/v1/auction/items/` | GameSection |
| `GET /api/v1/health/` | MetricsSection |
| `GET /api/v1/metrics/hourly/` | MetricsSection |
| `GET /api/v1/metrics/daily/` | MetricsSection |
| `GET /api/v1/metrics/performance/` | MetricsSection |
| `GET /api/v1/metrics/slow-queries/` | MetricsSection |
| `GET /api/v1/admin/config/` | AdminSection |
| `GET /api/v1/vapid-public-key/` | push.js |
| `POST/DELETE /api/v1/push-subscription/` | push.js |

---

## Implementado

| Endpoint | Onde no app |
|----------|--------------|
| `POST /api/v1/auth/login/` | Login; guarda `access` e `refresh`. |
| `POST /api/v1/auth/refresh/` | Renovação automática em 401 (helper `api.js` + `apiFetch`). |
| `POST /api/v1/auth/logout/` | Ao clicar em "Sair". |
| `GET /api/v1/user/game-data/?username=` | Card "Dados do jogo PDL" na seção Usuário. |
| `GET /api/v1/server/players-online/` | Detalhe "X jogadores reais" na seção Servidor. |
| `GET /api/v1/server/olympiad-current-heroes/` | Tabela "Heróis atuais da Olimpíada" na seção Servidor. |
| `GET /api/v1/server/raidboss-status/` | Bloco "Raid Bosses" na seção Servidor. |
| `GET /api/v1/server/siege-participants/<castle_id>/` | Botão "Ver participantes" em cada castelo no Siege. |
| `GET /api/v1/server/boss-jewel-locations/?ids=` | Card "Localizações Boss Jewels" na seção Servidor. |
| `GET /api/v1/discord/server/by-domain/` | Rodapé "Comunidade Discord: [nome]" quando há servidor para o domínio. |
