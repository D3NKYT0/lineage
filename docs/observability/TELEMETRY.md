# Telemetria (métricas Prometheus)

> **Última atualização:** 21/02/2026

O projeto expõe métricas no formato **Prometheus** para monitoramento (Grafana, Alertmanager, etc.).

## Ativação

No `.env` ou variáveis de ambiente:

```bash
TELEMETRY_ENABLED=True
```

Opcional:

- `TELEMETRY_METRICS_PATH` – path do endpoint (padrão: `/internal/metrics`)
- `TELEMETRY_SCRAPE_TOKEN` – token para scrape remoto (header `X-Metrics-Token`)

## Endpoint de métricas

- **URL**: `http(s)://seu-dominio/internal/metrics/`
- **Método**: GET
- **Formato**: texto Prometheus (`text/plain; version=0.0.4; charset=utf-8`)

### Quem pode acessar

- Usuário **staff** autenticado, ou
- Requisição de **localhost** (127.0.0.1, ::1), ou
- Requisição com header `X-Metrics-Token: <TELEMETRY_SCRAPE_TOKEN>` (se configurado)

## Métricas expostas

| Métrica | Tipo | Descrição | Labels |
|--------|------|-----------|--------|
| `pdl_http_requests_total` | Counter | Total de requisições HTTP | `method`, `path`, `status_class` (2xx, 4xx, 5xx) |
| `pdl_http_request_duration_seconds` | Histogram | Duração das requisições (segundos) | `method`, `path` |
| `pdl_business_events_total` | Counter | Eventos de negócio (wallet, payment, social, etc.) | `action`, `status` |

O **path** é normalizado para evitar cardinalidade alta (ex.: `/app/wallet/123/` → `/app/wallet/{id}`).

## Prometheus (scrape)

No `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'pdl'
    metrics_path: /internal/metrics
    static_configs:
      - targets: ['localhost:8000']
    # Se usar token (scrape remoto):
    # authorization:
    #   credentials: "SEU_TELEMETRY_SCRAPE_TOKEN"
    #   type: Bearer
    # Ou custom header (dependendo do Prometheus):
    # relabel_configs:
    #   - source_labels: __address__
    #     target_label: instance
```

Para scrape com token, use um sidecar ou config que envie o header `X-Metrics-Token`.

## Eventos de negócio nas métricas

Toda chamada a `log_action(logger, action, status, ...)` (ex.: `log_action(logger, "wallet_transfer_p2p", "sucesso", ...)`) também incrementa o contador `pdl_business_events_total{action="...", status="..."}` quando `TELEMETRY_ENABLED=True`. Assim você pode montar dashboards por ação (wallet_transfer_servidor, payment_mercadopago, social_post, etc.) e status (sucesso, erro, saldo_insuficiente, etc.).

## Exclusão de paths

Requisições a paths em `TELEMETRY_EXCLUDE_PATHS` não são contabilizadas. Padrão:

- `/static/`, `/media/`, `/favicon.ico`, `/__debug__/`, `/admin/jsi18n/`

Ajuste em `core/settings.py` se precisar.

## Dependência

Usa `prometheus_client` (já no `requirements.txt`). Se a lib não estiver disponível, o middleware e o endpoint não quebram; as métricas ficam apenas indisponíveis.

---

[ Voltar ao Índice](../INDEX.md)

