# Arquitetura de Observabilidade e Telemetria

> **Última atualização:** 21/02/2026

Documentação da infraestrutura de ponta a ponta do sistema PDL, abrangendo logs unificados, métricas de APIs exportáveis, mapeamento analítico e roteamento avançado do SPA no Webserver.

---

## 1. Sistema e Unificação de Logs

A padronização das saídas de erro e aviso da plataforma funciona de forma matricial para cruzamento com monitorias de servidor.

- **Padrão Transparente**: Logs físicos gerados acompanham carimbos ISO, Níveis (INFO, WARNING, ERROR), módulo e `request_id`.
- **Injeção de Identificação Única (Request ID)**: Todo tráfego HTTP pelo PDL gera um `X-Request-ID`. Middlewares atrelam nativamente essa chave aos Logs permitindo isolar do Ingress ao Database uma requisição em falha.
- **Utilitários Compartilhados**: `core.log_utils` possui o método construtor global `log_action()`, que abstrai saídas para eventos cruciais de negócio.

### Estrutura de Componentes
| Arquivo Base | Função Arquitetural |
|---------|-----------|
| `core/logger.py` | Controla handlers e formatação centralizada da biblioteca `logging` do Python. |
| `middlewares/request_id_middleware.py` | Middlewares para ancorar headers HTTP a variáveis de Thread locais. |
| `core/log_filters.py` | Filtros de ingestão (ex: plugar o Request ID ao contexto text-based). |

---

## 2. Telemetria Ativa Externamente (Node Prometheus)

A monitoria de tráfego, latência e anomalias de acesso estão orquestradas para leitura direta no padrão de mercado via coletores Prometheus.

### Mecânica Oculta
- **Métricas Exportáveis**: Endpoint universal pronto para ser indexado pelo Grafana e rastreado via Alertmanager (`/internal/metrics/`).
- **Interceptação Nível App**: Middleware exclusivo mapeia método HTTP, endpoint acionado e status num timer sub-segundo para relatórios de "HTTP Request Duration Histogram". 

### Indexadores de Monitoria
- `pdl_http_requests_total`: Carga de Requests / Throughput (agrupável por método e família do code class).
- `pdl_http_request_duration_seconds`: Aferidor estatístico de latência.
- `pdl_business_events_total`: Incrementadores críticos transacionais mapeados ao core.

*(Moduladores ativáveis por `TELEMETRY_ENABLED` na env).*

---

## 3. Monitoramento Interno Analítico API

Mesmo em ambientes isolados sem painéis robustos como o Grafana, o Painel Administrativo conta com engrenagens de Analytics REST diretamente persistidas no back-end via `APIMetricsMiddleware`:
- Dados demográficos agregam o volume total de acessos de rotas (Hits in Day/Hour) e tempo médio real em milissegundos.
- **Relatório de *Slow Queries***: Threshold em requisições HTTP que atinjam +1s são englobadas e isoladas no painel visualizando gargalos ou sobrecargas de queries N+1 latentes.

### Fallback e Resiliência
- **Health Check Nativo**: `/api/v1/health/` é blindado e indica a disponibilidade paralela de subsistemas chaves (Banco, Cache e status opcional/informativo do L2J Game Server isolado).
- Views expostas aos PWA (`Server Status` em `/api/v1/server/status/`) retornam payloads estruturados amigáveis (`{status: 'offline', online: 0}`) e falham suavemente contra timeout do Database ou L2J, evitando instabilidades gerais (HTTP 500) propagadas no cliente.

---

## 4. Invalidação de Cache no Edge (Webserver Tunning)

Na camada do proxy/webserver (NGINX), as configurações de entrega de conteúdo garantem versionamento correto das requisições via React PWA sem perder estabilidade offline:
- **No-Cache em Entradas SPA**: Toda entrada em `/static/pwa/index.html` passa a ser instruída ao Browser cliente via header `Cache-Control: no-cache`. Como o `index.html` vincula nomes com Hash únicos, as atualizações sistêmicas de CSS e JavaScript forçam novas renderizações instantaneamente enquanto desfrutam do Cache Extremo a Long-Prazo (Yearly) nos arquivos de base estrutural física (Chunks em memória).
- **Roteamento Híbrido SPA**: Declarações `location /pwa/` em `django.conf` do Nginx previnem NotFound (`404`) quando acessadas por URLs de Client-Side Navigation profundas, direcionando organicamente referências mortas ao loader via fallback.

---

## 5. Simulador Estocástico de Tráfego 

A base dispõe de ferramentas via console que agem como metralhadoras assíncronas projetadas para testar firewalls, cache warming e aferir logs.

```bash
# Executar a simulação de tráfego contra endpoints
python scripts/generate_api_traffic.py --base-url http://127.0.0.1:6085 --requests 100 --delay 0.1
```

---

[ Voltar ao Índice](../INDEX.md)

