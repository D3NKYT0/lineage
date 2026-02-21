# Melhorias Técnicas e Monitoramento

> **Última atualização:** 21/02/2026

Documentação das implementações técnicas e de infraestrutura do sistema PDL, abrangendo logs estruturados, telemetria avançada, painel de métricas da API, ajustes do PWA e otimizações gerais.

---

## 1. Sistema de Logs

### O que foi implementado

- **Formato padronizado**: logs em arquivo e console com timestamp ISO, nível, módulo e `request_id`.
- **Request ID**: cada requisição HTTP recebe um ID único (`X-Request-ID`), permitindo rastrear toda a cadeia de logs de uma requisição de ponta a ponta.
- **Helpers**: `core.log_utils` oferece `log_action()` e `get_logger()` para mensagens estruturadas e registro de eventos de negócio.

### Componentes Principais

| Arquivo | Função |
|---------|-----------|
| `core/logger.py` | Configuração central de formatters e handlers do Python logging |
| `middlewares/request_id_middleware.py` | Gera e injeta o `request_id` no contexto de cada requisição HTTP |
| `core/log_filters.py` | Filtros para incluir informações do request context (como o `request_id`) nos registros |
| `core/log_utils.py` | Funções utilitárias como `log_action()` e `get_logger()` |

### Uso

O mapeamento de ações com `log_action` está integrado aos módulos principais, como: carteira, pagamentos, rede social, notificações, lojas, leilões e licenciamento. Para mais informações, consulte a [Documentação de Logging](LOGGING.md).

---

## 2. Telemetria (Prometheus)

Para escalabilidade e monitoramento em tempo real, utilizamos o Prometheus para scraping de métricas.

### O que foi implementado

- **Métricas Exportáveis** para monitoramento externo via Grafana e geração de alertas via Alertmanager.
- **Middleware Dedicado** que captura duração, métodos, rotas e status de cada requisição HTTP.
- **Endpoint** `/internal/metrics/` expondo métricas nativamente no formato Prometheus.

### Métricas Disponíveis

| Métrica | Descrição |
|---------|-----------|
| `pdl_http_requests_total` | Total de requisições com labels (method, path, status_class) |
| `pdl_http_request_duration_seconds` | Histogram de distribuição de latência das requisições |
| `pdl_business_events_total` | Contadores para monitorar eventos críticos de negócio |

A telemetria pode ser ligada e desligada via variável de ambiente `TELEMETRY_ENABLED`. Consulte a [Documentação de Telemetria](TELEMETRY.md) para detalhes avançados.

---

## 3. Monitoramento da API

A estrutura da integração REST API foi robustecida com foco em estabilidade e métricas diretas no painel administrativo.

### Health Check de Serviços
- **Alta Disponibilidade**: O endpoint `/api/v1/health/` opera independentemente de bloqueios gerais e exibe o `uptime` global.
- **Isoladores de Falhas**: Serviços críticos (DB e Cache) influenciam a saúde do cluster; dependências secundárias (Game Server) são apenas informativas, não afetando o health check dos *load balancers*.

### Status do Servidor Analítico
- **Resiliência**: Serviços de leitura como o `Server Status` tratam exceções ativamente e retornam um fallback `{'status': 'offline', 'players_online': 0}` em vez de emitirem `HTTP 500`.

### Métricas Nativas e Analytics
Coleta feita internamente via `APIMetricsMiddleware`:
- **Consumo Estatístico**: Agregação de dados por hora/dia contemplando total de requisições, tempo médio, contabilidade de códigos de status HTTP e endpoints mais acessados.
- **Queries Lentas (Slow Queries)**: Mapeamento de instâncias onerosas (com tempo de execução superior a 1s).
- Os tempos são aferidos de modo unificado e expostos em `ms` para correta ingestão no frontend PWA.

---

## 4. PWA — Ajustes e Métricas

Foi feito tuning no painel PWA (Notificações Push / Admin) para interagir perfeitamente com o novo ecosistema REST:

- **Dashboard Integrado**: Normalização do parser dos objetos (`user/stats` e painéis de fallback). 
- **Confiabilidade**: O "Server Status" no UserSection agora lê estritamente `data.status` e `data.players_online`. Formatações de data utilizam fallbacks "—" apropriados quando o painel encontra propriedades vazias.
- **Aba de Métricas**: Refatorada para utilizar a nova modelagem de telemetria interna; lê os painéis de `health` dinamicamente para uptime global. Requer permissão explícita de `staff`.

---

## 5. Script de Geração de Tráfego

Para aferição de carga, testes de stress e validação do Grafana/Prometheus em ambientes de *staging*, a infraestrutura fornece o construtor `generate_api_traffic.py`.

```bash
python scripts/generate_api_traffic.py --base-url http://127.0.0.1:6085 --requests 50
```

Suporta flags comuns (`--delay`, `-q/--quiet`) para regulação do throttle dos testes.

---

## 6. Nginx — Invalidação de Cache e Servidão SPA

Foram aplicados tunings estruturais no webserver Nginx (`nginx/django.conf`):

- **Invalidação Transparente**: O arquivo de entrada principal `/static/pwa/index.html` passa a ser servido utilizando o cabeçalho estrito `Cache-Control: no-cache`. Como os bundles CSS/JS possuem content-hash, este setup garante que updates de versão sejam transparentes ao cliente, mas o container React se mantenha em long-term cache.
- **Roteamento SPA**: Correções da diretiva `location /pwa/`, estabelecendo um *fallback SPA* nativo para rotas do lado do cliente no React.

---

## 7. Mecânica Cross-cutting

### Warnings de Acesso Prematuro
O comportamento do `ResourcesConfig` foi reescrito. Chamadas que geravam `RuntimeWarning: Accessing the database during app initialization` no motor Django foram resolvidas deferindo o hook de setup. O motor de `populate_resources` não utiliza mais threads com delay estático, passando a atuar apenas sob a garantia segura do sinal sistêmico `request_started` emitido pela primeira chamada HTTP ou de comando no terminal. 

---

[ Voltar ao Índice](../INDEX.md)

