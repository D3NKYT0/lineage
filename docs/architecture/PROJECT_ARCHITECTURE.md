# Documento de Arquitetura do Projeto

> **Última atualização:** 21/02/2026

## 1. Visão Geral

O **Painel Definitivo Lineage (PDL)** é uma aplicação web robusta baseada em Django, com múltiplos módulos (apps) organizados por domínios de negócio. Utiliza Docker para orquestração do ambiente, facilitando desenvolvimento, testes e implantação. O frontend está desacoplado, com integração via REST API.

**Versão atual:** 1.17.x  
**Tecnologias principais:** Python 3.14, Django 5.2+, Gunicorn, Daphne, Celery, Redis, PostgreSQL, Nginx

---

## 2. Componentes Principais

### 2.1 Backend (Django)
- **Localização:** `apps/`, `core/`, `middlewares/`, `utils/`
- **Descrição:** O backend é implementado em Django, estruturado em múltiplos apps, cada um responsável por um domínio específico.
- **Recursos:** Autenticação, administração, relatórios, inventário, pagamentos, jogos, loja, wiki, notificações, assistente de IA, etc.
- **Middlewares customizados** (ex: AuditorMiddleware).
- **Utilitários** em `utils/`.

### 2.2 Apps do Projeto

#### Apps principais (`apps/main/`)
- **administrator** — Painel administrativo, configurações e temas
- **auditor** — Sistema de auditoria e logs
- **faq** — Perguntas frequentes
- **home** — Dashboard, autenticação e contas
- **message** — Mensagens e lista de amigos
- **news** — Notícias e blog
- **notification** — Notificações (push, email, in-app)
- **solicitation** — Solicitações e suporte
- **downloads** — Downloads (launcher, patches)
- **calendary** — Calendário de eventos
- **ai_assistant** — Assistente de IA
- **social** — Rede social e moderação
- **licence** — Sistema de licenciamento
- **resources** — Recursos compartilhados

#### Apps Lineage (`apps/lineage/`)
- **server** — Integração com servidor L2, rankings, bosses, cercos
- **wallet** — Carteira virtual
- **payment** — Pagamentos (Mercado Pago, Stripe, PayPal)
- **accountancy** — Contabilidade
- **inventory** — Inventário e itens
- **shop** — Loja virtual
- **marketplace** — Marketplace entre jogadores
- **auction** — Leilões
- **games** — Minigames (roleta, caixas, dados, pesca)
- **reports** — Relatórios e estatísticas
- **wiki** — Wiki de itens, monstros e quests
- **roadmap** — Roadmap público
- **tops** — Rankings (PvP, PK, Clan, Online)

#### Outros
- **api** — API REST pública
- **media_storage** — Gerenciamento de mídia

### 2.3 Frontend
- **Localização:** `frontend/`
- **Descrição:** Frontend desacoplado com integração via REST API.
- **Recursos:** Webpack, componentes JavaScript, gráficos (Charts.js).

### 2.4 Banco de Dados
- **PostgreSQL 15** — Banco principal (produção/Docker)
- **SQLite** — Opcional para desenvolvimento local
- **MySQL** — Banco do Lineage (conexão externa quando configurado)

### 2.5 Servidor Web e Proxy
- **Nginx** — Proxy reverso, arquivos estáticos e mídia
- **Gunicorn** — Requisições HTTP síncronas (site_http)
- **Daphne** — WebSockets e requisições assíncronas (site_asgi)
- **Configuração:** `nginx/`, `gunicorn-cfg.py`

### 2.6 Internacionalização
- **Localização:** `locale/`
- **Idiomas:** pt, en, es
- **Arquivos:** `.po` e `.mo`

### 2.7 Arquivos Estáticos e Mídia
- **static/** — CSS, JS, imagens, fontes
- **media/** — Uploads de usuários
- **themes/** — Temas personalizados

### 2.8 Testes e Scripts
- **test/** — Scripts e testes
- **setup/** — Automação de setup
- **install.sh** — Script principal de instalação

---

## 3. Orquestração com Docker Compose

### 3.1 Serviços Definidos
- **site_base** — Imagem base (build)
- **site_http** — Django com Gunicorn (requisições síncronas)
- **site_asgi** — Django com Daphne (WebSockets, assíncrono)
- **celery** — Worker de tarefas assíncronas
- **celery-beat** — Agendador de tarefas
- **flower** — Monitoramento do Celery
- **nginx** — Servidor web e proxy reverso (porta 6085)
- **redis** — Broker de mensagens e cache
- **postgres** — Banco de dados PostgreSQL 15

### 3.2 Rede e Volumes
- **Rede:** `lineage_network`
- **Volumes:** `static_data`, `media_data`, `logs_data`, `postgres_data`
- **Montagem de temas:** `./themes` em `/themes/installed/`

---

## 4. Estrutura de Diretórios

```
apps/           # Apps Django por domínio
core/           # Configurações centrais do projeto
middlewares/    # Middlewares customizados
utils/          # Utilitários e funções auxiliares
frontend/       # Código do frontend
static/         # Arquivos estáticos
media/          # Uploads
themes/         # Temas personalizados
nginx/          # Configurações do Nginx
locale/         # Traduções
templates/      # Templates Django
```

---

## 5. Fluxo de Requisições

1. Requisição HTTP → Nginx (porta 6085)
2. Nginx roteia para site_http (Gunicorn) ou site_asgi (Daphne) conforme o tipo
3. Django processa a requisição
4. Tarefas assíncronas são enfileiradas no Redis/Celery

---

## 6. Considerações de Segurança
- Variáveis de ambiente para segredos (`.env`, `env.sample`)
- Proxy reverso Nginx
- Autenticação JWT para API
- CORS configurado
- Rate limiting na API

---

## 7. Internacionalização e Acessibilidade
- Suporte a pt, en, es via `locale/`
- Variáveis de tema internacionalizadas
- Templates organizados para manutenção

---

## 8. Implantação e Escalabilidade
- Implantação via Docker Compose e `install.sh`
- Possibilidade de escalar workers (web, celery)
- Separação clara entre frontend e backend

---

## 9. Observabilidade e Logs
- Diretório `logs/` para logs da aplicação
- Flower para monitoramento do Celery
- Integração possível com ferramentas externas

---

## 10. Documentação
- `README.md` — Visão geral e instalação
- `workflow.md` — Fluxo de desenvolvimento
- `docs/` — Documentação técnica detalhada

---

[ Voltar ao Índice](../INDEX.md)

