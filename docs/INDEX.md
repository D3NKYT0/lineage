# 📚 Documentação — Painel Definitivo Lineage (PDL)

> **Última atualização:** 20/02/2026

> Índice geral da documentação. Para começar, consulte o [README do projeto](../README.md).

---

## 🧭 Por onde começar?

Escolha o guia adequado ao seu perfil:

| Você é... | Vá para... |
|-----------|-----------|
| 🧑 **Jogador / Usuário do Painel** | [Guia do Usuário Final](#-guia-do-usuário-final) |
| 🛠️ **Dono do Servidor / Admin** | [Guia do Administrador](#%EF%B8%8F-guia-do-administrador) |
| 👩‍💻 **Desenvolvedor / Técnico** | [Instalação](#-instalação-e-deploy) · [Arquitetura](#%EF%B8%8F-arquitetura) · [API](#-api-rest) |

---

## 🧑 Guia do Usuário Final
> Para jogadores que querem aprender a usar o painel PDL.

| Documento | Descrição |
|-----------|-----------|
| [GETTING_STARTED](user-guide/GETTING_STARTED.md) | 🚀 Primeiros passos: cadastro, login, vincular conta |
| [MASTER_ACCOUNT_SERVICES](user-guide/MASTER_ACCOUNT_SERVICES.md) | 📂 Criar sub-contas (Lineage 2) e gerenciar serviços (Unstuck, Nicks) |
| [WALLET_AND_PAYMENTS](user-guide/WALLET_AND_PAYMENTS.md) | 💰 Carteira, depósitos, transferências e fichas |
| [INVENTORY_PORTAL](user-guide/INVENTORY_PORTAL.md) | 🎒 Como usar o Web Inventory e retirar prêmios pro jogo |
| [SHOP_GUIDE](user-guide/SHOP_GUIDE.md) | 🛒 Como usar a Loja de Itens |
| [AUCTION_GUIDE](user-guide/AUCTION_GUIDE.md) | 🏷️ Como dar lances e criar leilões |
| [MARKETPLACE_USER_GUIDE](user-guide/MARKETPLACE_USER_GUIDE.md) | 🛍️ Comprar e vender personagens no Marketplace |
| [SOCIAL_USER_GUIDE](user-guide/SOCIAL_USER_GUIDE.md) | 📱 Rede social: posts, reações, hashtags |
| [SUPPORT_USER_GUIDE](user-guide/SUPPORT_USER_GUIDE.md) | 🎧 Central de Ajuda: tickets e atendimento IA |
| [TOPS_AND_GAME_STATS](user-guide/TOPS_AND_GAME_STATS.md) | 🏆 Estatísticas, rankings de PVP e Bosses |
| [NOTIFICATION_AND_MESSAGES](user-guide/NOTIFICATION_AND_MESSAGES.md) | 🔔 Notificações, chat e lista de amigos |

---

## 🛠️ Guia do Administrador
> Para donos de servidor que gerenciam o PDL.

| Documento | Descrição |
|-----------|-----------|
| [ADMIN_OVERVIEW](admin-guide/ADMIN_OVERVIEW.md) | 🗂️ Visão geral de todas as ferramentas de admin |
| [CONFIG_HUB_GUIDE](admin-guide/CONFIG_HUB_GUIDE.md) | ⚙️ Central de Configurações (Config Hub) e seus 25 Módulos Ocultos |
| [SHOP_ADMIN_GUIDE](admin-guide/SHOP_ADMIN_GUIDE.md) | 🛒 Gerenciar itens, pacotes e cupons de desconto |
| [PAYMENT_CONFIGURATION](admin-guide/PAYMENT_CONFIGURATION.md) | 💳 Configurar MercadoPago e Stripe |
| [ACCOUNTANCY_GUIDE](admin-guide/ACCOUNTANCY_GUIDE.md) | 📊 Relatórios financeiros e fluxo de caixa |
| [WIKI_ADMIN_GUIDE](admin-guide/WIKI_ADMIN_GUIDE.md) | 📚 Criar páginas e patch notes na Wiki |
| [CALENDARY_GUIDE](admin-guide/CALENDARY_GUIDE.md) | 📅 Gerenciar eventos no calendário |
| [ROADMAP_ADMIN_GUIDE](admin-guide/ROADMAP_ADMIN_GUIDE.md) | 🗺️ Publicar planos de desenvolvimento |
| [NEWS_AND_FAQ_GUIDE](admin-guide/NEWS_AND_FAQ_GUIDE.md) | 📰 Publicar notícias e gerenciar FAQ |
| [HELPDESK_ADMIN_GUIDE](admin-guide/HELPDESK_ADMIN_GUIDE.md) | 🎧 Gerenciar abertura de tickets e atendimento |
| [MODERATION_ADMIN_GUIDE](admin-guide/MODERATION_ADMIN_GUIDE.md) | 🛡️ Aplicar banimentos e deletar logs sociais |
| [AUDITOR_ADMIN_GUIDE](admin-guide/AUDITOR_ADMIN_GUIDE.md) | 🕵️ Rastrear logs de fraude, Múltiplas Contas (IP) e financeiro |
| [DOWNLOADS_MANAGER_GUIDE](admin-guide/DOWNLOADS_MANAGER_GUIDE.md) | ⬇️ Configurar links (Mega, Drive) pro Client Lineage 2 |
| [THEMES_ADMIN_GUIDE](admin-guide/THEMES_ADMIN_GUIDE.md) | 🎨 Configurar templates e Dark/Light Mode |

---

## 🏛️ Arquitetura
> Visão geral da estrutura e diagramas do projeto.

| Documento | Descrição |
|-----------|-----------|
| [PROJECT_ARCHITECTURE](architecture/PROJECT_ARCHITECTURE.md) | Visão geral da arquitetura do projeto |
| [ARCHITECTURE_OVERVIEW_DIAGRAM](architecture/ARCHITECTURE_OVERVIEW_DIAGRAM.md) | Diagrama de arquitetura geral |
| [LINEAGE2_DB_INTEGRATION_DIAGRAM](architecture/LINEAGE2_DB_INTEGRATION_DIAGRAM.md) | Diagrama de integração com banco Lineage 2 |
| [THEME_SYSTEM_FLOW_DIAGRAM](architecture/THEME_SYSTEM_FLOW_DIAGRAM.md) | Diagrama do fluxo do sistema de temas |
| [MULTI_SERVER_ARCHITECTURE](architecture/MULTI_SERVER_ARCHITECTURE.md) | Arquitetura Matriz-Filial para Múltiplos Servidores |

---

## 🚀 Instalação e Deploy
> Instalação, configuração de ambiente, variáveis e infraestrutura.

| Documento | Descrição |
|-----------|-----------|
| [INSTALLATION_AND_DEPLOY](installation/INSTALLATION_AND_DEPLOY.md) | Guia de instalação e deploy |
| [INSTALL_SH_GUIDE](installation/INSTALL_SH_GUIDE.md) | Guia completo do script install.sh |
| [DEVELOPMENT_GUIDE](installation/DEVELOPMENT_GUIDE.md) | Guia de desenvolvimento local |
| [VARIABLES_ENVIRONMENT](installation/VARIABLES_ENVIRONMENT.md) | Variáveis de ambiente (.env) |
| [FFMPEG_SETUP](installation/FFMPEG_SETUP.md) | Configuração do FFmpeg |
| [FAVICON_SETUP](installation/FAVICON_SETUP.md) | Configuração do favicon |
| [MEDIA_STORAGE_SETUP](installation/MEDIA_STORAGE_SETUP.md) | Configuração de armazenamento de mídia |
| [AWS_S3_SETUP](installation/AWS_S3_SETUP.md) | Configuração do AWS S3 |
| [DATABASE_CONNECTION_POOLING](installation/DATABASE_CONNECTION_POOLING.md) | Configuração de pool de conexões ao banco |

---

## 🔌 API REST
> Documentação da API pública e endpoints disponíveis.

| Documento | Descrição |
|-----------|-----------|
| [API_DOCUMENTATION](api/API_DOCUMENTATION.md) | Documentação completa da API |
| [API_ENDPOINTS](api/API_ENDPOINTS.md) | Lista de endpoints disponíveis |
| [API_CONFIG_PANEL](api/API_CONFIG_PANEL.md) | Configuração da API via painel |
| [README_API](api/README_API.md) | README do app de API |
| [REST_API_GUIDE](api/REST_API_GUIDE.md) | Guia rápido da API REST |

---

## 🎨 Sistema de Temas
> Criação, instalação e customização de temas.

| Documento | Descrição |
|-----------|-----------|
| [THEME_SYSTEM](themes/THEME_SYSTEM.md) | Visão geral do sistema de temas |
| [DESIGN_SYSTEM](themes/DESIGN_SYSTEM.md) | Guia completo de Design System da Plataforma |
| [THEME_DEVELOPER_GUIDE](themes/THEME_DEVELOPER_GUIDE.md) | Guia para desenvolvedores de temas |
| [GUIDE_CREATE_THEME](themes/GUIDE_CREATE_THEME.md) | Tutorial completo para criar um tema |
| [THEME_ERROR_HANDLING](themes/THEME_ERROR_HANDLING.md) | Tratamento de erros em temas |
| [THEME_TEMPLATES_ROUTES](themes/THEME_TEMPLATES_ROUTES.md) | Rotas e templates do sistema de temas |

---

## ⚙️ Funcionalidades
> Módulos e features do painel.

| Documento | Descrição |
|-----------|-----------|
| [MARKETPLACE](features/MARKETPLACE.md) | Sistema de marketplace entre jogadores |
| [INFLATION_SYSTEM](features/INFLATION_SYSTEM.md) | Sistema anti-inflação |
| [PURCHASE_BONUS_SYSTEM](features/PURCHASE_BONUS_SYSTEM.md) | Sistema de bônus em compras |
| [MODERATION_SYSTEM](features/MODERATION_SYSTEM.md) | Sistema de moderação |
| [MODERATION_NOTIFICATION_SYSTEM](features/MODERATION_NOTIFICATION_SYSTEM.md) | Notificações do sistema de moderação |
| [FLOATING_NOTIFICATIONS_SYSTEM](features/FLOATING_NOTIFICATIONS_SYSTEM.md) | Notificações flutuantes |
| [SOCIAL_NETWORK_GUIDE](features/SOCIAL_NETWORK_GUIDE.md) | Guia da rede social integrada |
| [FRIENDS_SYSTEM](features/FRIENDS_SYSTEM.md) | Sistema e Otimização da Lista de Amigos |
| [MULTI_ACCOUNT_MANAGEMENT](features/MULTI_ACCOUNT_MANAGEMENT.md) | Gerenciamento de múltiplas contas |
| [LICENSE_SYSTEM](features/LICENSE_SYSTEM.md) | Sistema de licenciamento (Geral) |
| [BANNER_CONFIGURATION](features/BANNER_CONFIGURATION.md) | Configuração de banners |
| [SHOW_PLAYERS_ONLINE_CONFIG](features/SHOW_PLAYERS_ONLINE_CONFIG.md) | Exibição de jogadores online |
| [GRANDBOSS_TIME_CONFIG](features/GRANDBOSS_TIME_CONFIG.md) | Configuração de horários de Grand Boss |
| [INTERNAL_DOWNLOADS](features/INTERNAL_DOWNLOADS.md) | Sistema de downloads internos |
| [FINANCIAL_USER_GUIDE](features/FINANCIAL_USER_GUIDE.md) | Guia financeiro para usuários |
| [DISCORD_BOT_INTEGRATION](features/DISCORD_BOT_INTEGRATION.md) | Integração com bot Discord |
| [HELPDESK_SYSTEM](features/HELPDESK_SYSTEM.md) | Sistema de Helpdesk e Chamados |
| [AI_ASSISTANT](features/AI_ASSISTANT.md) | Assistente Virtual de Inteligência Artificial |

---

## 🎮 Minigames
> Jogos integrados ao painel.

| Documento | Descrição |
|-----------|-----------|
| [MINIGAMES_GUIDE](games/MINIGAMES_GUIDE.md) | Guia do Ecossistema de Minigames |

---

## 🔒 Segurança e Autenticação
> Login, CAPTCHA, OAuth e modelo de segurança.

| Documento | Descrição |
|-----------|-----------|
| [DJANGO_L2_SECURITY_MODEL](security/DJANGO_L2_SECURITY_MODEL.md) | Modelo de segurança Django + Lineage 2 |
| [CAPTCHA_LOGIN_SYSTEM](security/CAPTCHA_LOGIN_SYSTEM.md) | Sistema de CAPTCHA no login |
| [SOCIAL_LOGIN_CONFIG](security/SOCIAL_LOGIN_CONFIG.md) | Configuração de login social |

---

## 🔗 Integração com Lineage 2
> Integração com servidor L2, migrações e filtros.

| Documento | Descrição |
|-----------|-----------|
| [LINEAGE_SERVER_INTEGRATION](integration/LINEAGE_SERVER_INTEGRATION.md) | Integração com servidor Lineage 2 |
| [MIGRATION_L2_TO_PDL](integration/MIGRATION_L2_TO_PDL.md) | Migração de dados L2 para o PDL |
| [README_MIGRATION](integration/README_MIGRATION.md) | README de migrações |
| [RETROACTIVE_FILTERS](integration/RETROACTIVE_FILTERS.md) | Filtros retroativos de dados |

---

## 🖼️ Mídia e Armazenamento
> Gerenciamento de arquivos, imagens e armazenamento em nuvem.

| Documento | Descrição |
|-----------|-----------|
| [README_MEDIA_APP](media/README_MEDIA_APP.md) | README do app de mídia |
| [README_S3](media/README_S3.md) | Integração com AWS S3 |
| [MEDIA_CLEANUP_COMMANDS](media/MEDIA_CLEANUP_COMMANDS.md) | Comandos de limpeza de mídia |

---

## 🔔 Notificações
> Sistema de notificações e news.

| Documento | Descrição |
|-----------|-----------|
| [NOTIFICATIONS_README](notifications/NOTIFICATIONS_README.md) | Sistema de notificações |
| [VISUAL_AND_SOCIAL_UPDATES](notifications/VISUAL_AND_SOCIAL_UPDATES.md) | Nova Era Visual e Rede Social |

---

## 🏆 Rankings (Tops)
> Tabelas de ranking e tops de jogadores.

| Documento | Descrição |
|-----------|-----------|
| [README_TOPS](tops/README_TOPS.md) | Sistema de tops e rankings |
| [TOPS_HUB_UI_GUIDE](tops/TOPS_HUB_UI_GUIDE.md) | Guia de Interface e Interatividade do Hub |

---

## 🛡️ Moderação
> Ferramentas de moderação e exportação de logs.

| Documento | Descrição |
|-----------|-----------|
| [EXPORT_MODERATION_LOGS](moderation/EXPORT_MODERATION_LOGS.md) | Exportação de logs de moderação |
| [HOW_TO_TEST_MODERATION](moderation/HOW_TO_TEST_MODERATION.md) | Como testar o sistema de moderação |

---

## 🛠️ Administração Django
> Comandos customizados e ferramentas administrativas.

| Documento | Descrição |
|-----------|-----------|
| [CUSTOM_COMMANDS](admin/CUSTOM_COMMANDS.md) | Comandos customizados do Django |
| [QUERY_GENERATOR_DOCUMENTATION](admin/QUERY_GENERATOR_DOCUMENTATION.md) | Gerador de queries SQL |

---

## 📊 Observabilidade
> Logging, telemetria e monitoramento.

| Documento | Descrição |
|-----------|-----------|
| [LOGGING](observability/LOGGING.md) | Sistema de logging |
| [TELEMETRY](observability/TELEMETRY.md) | Telemetria e métricas |
| [OBSERVABILITY_ARCHITECTURE](observability/OBSERVABILITY_ARCHITECTURE.md) | Arquitetura de Observabilidade e Telemetria |

---

## 📱 PWA (Progressive Web App)
> Análise e planejamento da versão PWA.

| Documento | Descrição |
|-----------|-----------|
| [PWA_TECHNICAL_ANALYSIS](pwa/PWA_TECHNICAL_ANALYSIS.md) | Análise técnica da PWA |
| [PWA_EXECUTIVE_SUMMARY](pwa/PWA_EXECUTIVE_SUMMARY.md) | Resumo executivo da PWA |



## 🔧 Troubleshooting
> Diagnóstico e resolução de problemas.

| Documento | Descrição |
|-----------|-----------|
| [DEBUGGING_GUIDE](troubleshooting/DEBUGGING_GUIDE.md) | Guia geral de diagnósticos e debugging da aplicação |

---

## 📝 Artigos
> Materiais educativos e artigos técnicos.

| Documento | Descrição |
|-----------|-----------|
| [AI_PDL_ARTICLE](articles/AI_PDL_ARTICLE.md) | Artigo sobre IA no PDL |

---

> 💡 **Dica:** Todos os documentos são gerados a partir do código-fonte e atualizados a cada release.
