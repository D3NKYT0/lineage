# Changelog — Melhorias Técnicas e Monitoramento (Fev 2026)

Documentação das alterações realizadas no sistema PDL: logs, telemetria, API, PWA e ajustes técnicos.

---

## 1. Sistema de Logs

### O que mudou

- **Formato padronizado**: logs em arquivo e console com timestamp ISO, nível, módulo e `request_id`.
- **Request ID**: cada requisição HTTP recebe um ID único (`X-Request-ID`), permitindo rastrear toda a cadeia de logs de uma requisição.
- **Helpers**: `core.log_utils` oferece `log_action()` e `get_logger()` para mensagens estruturadas.

### Arquivos principais

| Arquivo | Descrição |
|---------|-----------|
| `core/logger.py` | Configuração de formatters e handlers |
| `middlewares/request_id_middleware.py` | Middleware que gera o `request_id` por requisição |
| `core/log_filters.py` | Filtros para incluir `request_id` nos registros |
| `core/log_utils.py` | `log_action()`, `get_logger()` |

### Uso de `log_action`

Integrado em apps como: wallet, payment, social, notification, message, shop, auction, licence.

### Documentação

- `docs/LOGGING.md`

---

## 2. Telemetria (Prometheus)

### O que mudou

- **Métricas Prometheus** para monitoramento externo (Grafana, Alertmanager).
- **Middleware** que registra duração e status de cada requisição HTTP.
- **Endpoint** `/internal/metrics/` expondo métricas em formato Prometheus.

### Métricas expostas

| Métrica | Descrição |
|---------|-----------|
| `pdl_http_requests_total` | Total de requisições (labels: method, path, status_class) |
| `pdl_http_request_duration_seconds` | Histogram de duração das requisições |
| `pdl_business_events_total` | Eventos de negócio (wallet, payment, social, etc.) |

### Ativação

```bash
TELEMETRY_ENABLED=True
```

### Arquivos principais

| Arquivo | Descrição |
|---------|-----------|
| `core/telemetry.py` | Definição das métricas |
| `middlewares/telemetry_middleware.py` | Registro de requisições HTTP |
| `core/telemetry_views.py` | Endpoint `/internal/metrics/` |

### Documentação

- `docs/TELEMETRY.md`

---

## 3. Melhorias na API

### Health Check

- **Sempre ativo**: endpoint `/api/v1/health/` não depende mais de `ApiEndpointToggle`.
- **Uptime**: resposta passa a incluir `uptime` (segundos desde o início do processo).
- **Tratamento de erros**: DB e cache tratados como críticos; game server é informativo (não derruba o health para load balancers).

### Server Status

- **Resposta estável**: sempre retorna HTTP 200; em erro retorna `status: 'offline'` e `players_online: 0`.

### Métricas da API

- **APIMetricsMiddleware**: novo middleware que registra todas as requisições `/api/` para a aba de métricas.
- **Métricas por hora/dia**: total de requisições, tempo médio, taxa de erro, status codes e endpoints.
- **Performance por endpoint**: tempo médio e contagem por rota.
- **Queries lentas**: listagem de requisições com duração > 1s.

### Formato dos dados

- Performance: inclusão de `avg_time` (compatível com o PWA).
- Slow queries: inclusão de `execution_time` e `time` em ms.

---

## 4. PWA — Ajustes e Métricas

### UserSection

- **Dashboard/Profile**: parsing normalizado para respostas da API (objeto plano do dashboard, profile como fallback).
- **Server Status**: leitura correta de `data.status` e `data.players_online`.
- **Estatísticas do jogo**: montagem a partir de `user/stats` e dashboard.
- **Fallbacks**: remoção de valores fictícios (ex.: "admin").
- **Datas**: `formatDate` exibe "—" quando não há data.

### Aba Métricas

- **Health**: uso de `health.data?.status` e `health.data?.uptime`.
- **Integração**: exibição correta de métricas horárias, diárias, performance e queries lentas (exige usuário staff).

### Deploy

```bash
cd frontend/pwa-push && npm install && npm run deploy
```

---

## 5. Script de Geração de Tráfego

Criado `scripts/generate_api_traffic.py` para popular métricas da API.

### Uso

```bash
python scripts/generate_api_traffic.py --base-url http://127.0.0.1:6085 --requests 50
```

### Opções

| Opção | Descrição |
|-------|-----------|
| `--base-url` | URL base do servidor |
| `--requests`, `-n` | Número de requisições |
| `--delay` | Intervalo entre requisições (segundos) |
| `--quiet`, `-q` | Modo silencioso |

---

## 6. Nginx — PWA e Cache

### Alterações em `nginx/django.conf`

- **`/static/pwa/index.html`**: `Cache-Control: no-cache` para garantir que novo build seja sempre baixado (referência ao bundle muda a cada deploy).
- **`location /pwa/`**: corrigida para `location /pwa/` com `alias` adequado e fallback SPA para `/static/pwa/index.html`.

---

## 7. Ajustes Técnicos

### ResourcesConfig — Warning de Inicialização

- **Problema**: `RuntimeWarning: Accessing the database during app initialization`.
- **Solução**: `populate_resources` passa a rodar no sinal `request_started` (primeiro request) em vez de thread com delay, evitando acesso ao banco durante a inicialização.

---

## Arquivos Modificados/Criados (Resumo)

| Tipo | Arquivos |
|------|----------|
| **Logs** | `core/logger.py`, `core/log_filters.py`, `core/log_utils.py`, `middlewares/request_id_middleware.py` |
| **Telemetria** | `core/telemetry.py`, `core/telemetry_views.py`, `middlewares/telemetry_middleware.py` |
| **API** | `apps/api/monitoring.py`, `middlewares/api_metrics_middleware.py`, `apps/api/views.py` |
| **PWA** | `frontend/pwa-push/src/UserSection.js`, `frontend/pwa-push/src/MetricsSection.js` |
| **Infra** | `core/settings.py`, `nginx/django.conf` |
| **Scripts** | `scripts/generate_api_traffic.py` |
| **Apps** | `apps/main/resources/apps.py` |
| **Docs** | `docs/LOGGING.md`, `docs/TELEMETRY.md`, `docs/CHANGELOG_2026_02.md` |
