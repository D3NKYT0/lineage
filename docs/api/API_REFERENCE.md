# 📚 Referência Completa da API

> **Última atualização:** 21/02/2026

Listagem completa e técnica de todos os endpoints suportados pela API Lineage 2 PDL.
Não esqueça de verificar a [página inicial (README)](README.md) para detalhes de Base URL e Autenticação.

## Índice de Endpoints

1. [Autenticação e Sessão](#1-autenticação-e-sessão-🔒)
2. [Usuário da API Principal](#2-usuário-da-api-principal-👤)
3. [Estatísticas de Conta Lineage (`/api/accounts/`)](#3-estatísticas-de-conta-lineage-apiaccounts-🛡️)
4. [Status e Dados do Servidor](#4-status-e-dados-do-servidor-🖥️)
5. [Olimpíada e Bosses](#5-olimpíada-e-bosses-🐉)
6. [Busca e Clãs](#6-busca-e-clãs-🔍)
7. [Métricas e Monitoramento](#7-métricas-e-monitoramento-📊)
8. [Administração e Integrações Externas](#8-administração-e-integrações-externas-⚙️)

---

## 1. Autenticação e Sessão 🔒

Todos os endpoints principais de `/auth` são servidos na versão v1 (`/api/v1/auth/`).

### Gerar Tokens (Login)
`POST /api/v1/auth/login/`
* **Autenticação:** Pública
* **Body Request:**
  ```json
  {
      "username": "seu_usuario",
      "password": "sua_senha"
  }
  ```
* **Response:** `{ "access": "...", "refresh": "...", "user_id": 1, "username": "...", "message": "Success" }`

### Renovar Access Token (Refresh)
`POST /api/v1/auth/refresh/`
* **Autenticação:** Pública
* **Body Request:** `{ "refresh": "seu_refresh_token" }`

### Encerrar Sessão (Logout)
`POST /api/v1/auth/logout/` 🔒
* **Autenticação:** Bearer Token Obrigatório
* **Body Request:** `{ "refresh": "seu_refresh_token" }`
* **Descrição:** Blacklista permanentemente o `refresh` token atual.

---

## 2. Usuário da API Principal 👤

Endereçados em `/api/v1/user/`. Todas as chamadas necessitam de Token JWT Válido no HTTP Header.

### Obter / Editar Perfil
* **Visualizar:** `GET /api/v1/user/profile/` 🔒
* **Editar:** `PUT /api/v1/user/profile/` 🔒
  * **Body:** `{ "first_name": "Novo", "last_name": "Sobrenome", "email": "novo@email.com" }`

### Alterar Senha (API User)
`POST /api/v1/user/change-password/` 🔒
* **Body Request:** `{ "old_password": "...", "new_password": "...", "confirm_password": "..." }`

### Dashboards e Status Pessoal
* **Mural (Dashboard Geral):** `GET /api/v1/user/dashboard/` 🔒
* **Estatísticas Rápidas:** `GET /api/v1/user/stats/` 🔒
* **Dados Pessoais In-Game:** `GET /api/v1/user/game-data/` 🔒

---

## 3. Estatísticas de Conta Lineage (`/api/accounts/`) 🛡️

Estes endpoints não usam `/v1/`, eles são atrelados às contas ingame. As rotas partem de `/api/accounts/`. Muitos deles interagem ativamente com a bridge L2.

* **Dashboard de Contas:** `GET /api/accounts/dashboard/` 🔒
* **Atualização Ingame de Senha:** `POST /api/accounts/update_password/` 🔒
* **Registro de Conta L2:** `POST /api/accounts/register/` 🔒
* **Sincronizar/Ligar Contas:** `POST /api/accounts/link/` 🔒
* **Solicitar Token de Link (Por E-mail):** `POST /api/accounts/request_link/`
* **Validar Link com Token:** `POST /api/accounts/link_by_token/`

---

## 4. Status e Dados do Servidor 🖥️

Endereçados em `/api/v1/server/`.

### Status Básicos
* **Verificar Status Geral:** `GET /api/v1/server/status/`
* **Contagem de Jogadores:** `GET /api/v1/server/players-online/`
  * *Response:* `{ "online_count": 150, "fake_players": ..., "real_players": ... }`
* **Server Info (Metadata público):** `GET /api/v1/server/info/`

### Top Ranking / Liderança
Aceitam o Query Parameter `?limit=10`
* **Top PvP:** `GET /api/v1/server/top-pvp/`
* **Top PK:** `GET /api/v1/server/top-pk/`
* **Melhores Clãs:** `GET /api/v1/server/top-clan/`
* **Jogadores mais ricos:** `GET /api/v1/server/top-rich/`
* **Maior Tempo Logado:** `GET /api/v1/server/top-online/`
* **Maior Nível Geral:** `GET /api/v1/server/top-level/`

* **Geral Score/Leaderboard:** `GET /api/v1/game/leaderboard/`
* **Geral Summary:** `GET /api/v1/game/summary/`

---

## 5. Olimpíada e Bosses 🐉

Endereçados em `/api/v1/server/`.

### Olimpíada 🏅
* **Ranking Vigente:** `GET /api/v1/server/olympiad-ranking/`
* **Heróis Atuais no Mês:** `GET /api/v1/server/olympiad-current-heroes/`
* **Todos os Heróis Históricos:** `GET /api/v1/server/olympiad-all-heroes/`

### Monstros e Raid Bosses
* **Status dos Grands Bosses (Epic):** `GET /api/v1/server/grandboss-status/`
* **Status de Raid Bosses (Gerais):** `GET /api/v1/server/raidboss-status/`
* **Geolocalização (Jewels Boss):** `GET /api/v1/server/boss-jewel-locations/?ids=X,Y,Z`

### Cercos a Castelos (Siege) 🏰
* **Visão Geral e Datas:** `GET /api/v1/server/siege/`
* **Clãs Inscritos e Status no Castelo (1-9):** `GET /api/v1/server/siege-participants/<castle_id>/`

---

## 6. Busca e Clãs 🔍

Buscas ativas de banco de dados por nomes de Entidades In-Game.

* **Buscar Personagem por Nome:** `GET /api/v1/search/character/?q=NomeChar`
* **Buscar Descrição e Preços de Item:** `GET /api/v1/search/item/?q=NomeDoItem`
* **Exibir Dados e Membros de um Clã:** `GET /api/v1/clan/<clan_name>/`
* **Prateleiras de Leilões (Leilão Global/Local):** `GET /api/v1/auction/items/?limit=20`

---

## 7. Métricas e Monitoramento 📊

Rotas utilizadas geralmente por dashboards analíticos externos (ex: Grafana/Prometheus). Todas as rotas suportam apenas requisições tipo GET. (Localizadas em `/api/v1/metrics/` ou `/api/v1/health/`)

* **Healthcheck do Sistema:** `GET /api/v1/health/`
* **Métricas do Servidor L2 (Por Hora):** `GET /api/v1/metrics/hourly/`
* **Métricas do Servidor L2 (Por Dia):** `GET /api/v1/metrics/daily/`
* **Desempenho da Web API e Tempo de Resposta:** `GET /api/v1/metrics/performance/`
* **Log de Queries Pesadas BD (Debugging Admin):** `GET /api/v1/metrics/slow-queries/` 🔒 *(Admin/Staff Only)*

---

## 8. Administração e Integrações Externas ⚙️

Endpoints administrativos diversos e conexões com aplicativos terceiros.

### Configurações de Servidor WEB
* **Informações Genéricas Web API:** `GET /api/v1/`
* **Resumo de Configurações API:** `GET /api/v1/admin/config/` 🔒 *(Admin)*
* **Visualizar Painel Frontal Admin API:** `GET /api/v1/admin/config/panel/` 🔒 *(Admin)*
* **Dashboard Completo de Resumo Administrativo:** `GET /api/v1/admin/dashboard/` 🔒 *(Admin)*

### Web Push Notifications
* **Coletar Vapid Key Publica da API:** `GET /api/v1/vapid-public-key/`
* **Inscrever Subscription de Notificação FrontEnd Web:** `POST /api/v1/push-subscription/`

### Discord Bot Endpoints
* **Recuperar Info do Servidor L2 para Discord:** `GET /api/v1/discord/server/`
* **Mapeamento/Info Especiais de Webhooks via Dominio:** `GET /api/v1/discord/server/by-domain/`

---

[ Voltar ao Índice](../INDEX.md)

