# 🛠️ Visão Geral do Painel de Administração

> **Última atualização:** 21/02/2026

Este guia oferece uma visão geral de todas as ferramentas disponíveis para administradores do servidor PDL.

---

## 1. Quem é um Administrador?

No PDL, um **Administrador** é um usuário Django com `is_staff=True`. Dependendo das permissões, pode ter acesso a módulos específicos ou acesso total via `/admin/`.

### Criando um Administrador
```bash
# Via Django shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(username='seunome')
>>> user.is_staff = True
>>> user.save()
```

Ou direto pelo Django Admin: `/admin/auth/user/<id>/change/`.

---

## 2. Áreas de Gerenciamento

| Área | URL | O que gerencia |
|------|-----|----------------|
| 🛒 **Loja** | `/app/shop/manager/` | Itens, pacotes, promoções |
| 📊 **Financeiro** | `/app/accountancy/` | Relatórios, saldos, fluxo de caixa |
| 💰 **Carteira** | `/app/wallet/config/coins/` | Configuração das moedas do jogo |
| 📅 **Calendário** | `/app/calendary/manager/` | Eventos do servidor |
| 🗺️ **Roadmap** | `/app/roadmap/manager/` | Planos e status de desenvolvimento |
| 📰 **Notícias** | `/admin/news/` | Publicações e comunicados |
| ❓ **FAQ** | `/admin/faq/` | Perguntas frequentes |
| 📚 **Wiki** | `/admin/wiki/` | Páginas do wiki do servidor |
| 🛡️ **Moderação** | `/admin/` | Filtros, denúncias, ações |
| 🔔 **Notificações** | `/admin/notification/` | Envio de notificações em massa |
| 🤖 **IA** | `/app/ai_assistant/` | Configuração do assistente IA |
| 📈 **Telemetria** | `/internal/metrics/` | Métricas Prometheus |
| 🧰 **Comandos** | Terminal (`manage.py`) | Comandos administrativos |

---

## 3. Django Admin (/admin/)

O Django Admin nativo (`/admin/`) é acessível a superusuários e dá acesso total a todos os modelos do sistema. Use para:
- Gerenciar usuários e permissões
- Administrar qualquer modelo do sistema diretamente
- Ações em lote (ex: ativar/desativar múltiplos registros)

---

## 4. Painel de Monitoramento

### Logs
O sistema gera logs estruturados em arquivo e console. Consulte [`LOGGING.md`](../observability/LOGGING.md) para mais detalhes.

### Telemetria (Prometheus)
Se `TELEMETRY_ENABLED=True` no `.env`, acesse métricas em `/internal/metrics/`. Consulte [`TELEMETRY.md`](../observability/TELEMETRY.md).

---

## 5. Comandos Úteis (CLI)

| Comando | O que faz |
|---------|-----------|
| `python manage.py migrate` | Aplica migrações do banco de dados |
| `python manage.py collectstatic` | Coleta arquivos estáticos |
| `python manage.py createsuperuser` | Cria um superusuário |
| `python manage.py shell` | Shell interativo Django |

Consulte todos os comandos customizados em [`CUSTOM_COMMANDS.md`](../admin/CUSTOM_COMMANDS.md).

---

## 6. Documentos por Área

### Para Administradores de Servidor
- [Loja — Gerenciamento](SHOP_ADMIN_GUIDE.md)
- [Pagamentos — Configuração](PAYMENT_CONFIGURATION.md)
- [Relatórios Financeiros](ACCOUNTANCY_GUIDE.md)
- [Calendário de Eventos](CALENDARY_GUIDE.md)
- [Roadmap do Servidor](ROADMAP_ADMIN_GUIDE.md)
- [Wiki do Servidor](WIKI_ADMIN_GUIDE.md)
- [Notícias e FAQ](NEWS_AND_FAQ_GUIDE.md)

### Para Administradores Técnicos
- [Arquitetura do Projeto](../architecture/PROJECT_ARCHITECTURE.md)
- [Instalação e Deploy](../installation/INSTALLATION_AND_DEPLOY.md)
- [Variáveis de Ambiente](../installation/VARIABLES_ENVIRONMENT.md)
- [Logging e Observabilidade](../observability/LOGGING.md)

---

[ Voltar ao Índice](../INDEX.md)

