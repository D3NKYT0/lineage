# 📚 Documentação — Painel Definitivo Lineage (PDL)

> Índice geral da documentação. Para começar, consulte o [README do projeto](../README.md).

---

## 🏛️ Arquitetura
> Visão geral da estrutura e diagramas do projeto.

| Documento | Descrição |
|-----------|-----------|
| [PROJECT_ARCHITECTURE](architecture/PROJECT_ARCHITECTURE.md) | Visão geral da arquitetura do projeto |
| [ARCHITECTURE_OVERVIEW_DIAGRAM](architecture/ARCHITECTURE_OVERVIEW_DIAGRAM.md) | Diagrama de arquitetura geral |
| [LINEAGE2_DB_INTEGRATION_DIAGRAM](architecture/LINEAGE2_DB_INTEGRATION_DIAGRAM.md) | Diagrama de integração com banco Lineage 2 |
| [THEME_SYSTEM_FLOW_DIAGRAM](architecture/THEME_SYSTEM_FLOW_DIAGRAM.md) | Diagrama do fluxo do sistema de temas |

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
| [API_IMPLEMENTATION_SUMMARY](api/API_IMPLEMENTATION_SUMMARY.md) | Resumo de implementação da API |
| [README_API](api/README_API.md) | README do app de API |
| [REST_API_GUIDE](api/REST_API_GUIDE.md) | Guia rápido da API REST |

---

## 🎨 Sistema de Temas
> Criação, instalação e customização de temas.

| Documento | Descrição |
|-----------|-----------|
| [THEME_SYSTEM](themes/THEME_SYSTEM.md) | Visão geral do sistema de temas |
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
| [SISTEMA_BONUS_COMPRAS](features/SISTEMA_BONUS_COMPRAS.md) | Sistema de bônus em compras |
| [SISTEMA_MODERACAO](features/SISTEMA_MODERACAO.md) | Sistema de moderação |
| [SISTEMA_NOTIFICACAO_MODERACAO](features/SISTEMA_NOTIFICACAO_MODERACAO.md) | Notificações do sistema de moderação |
| [SISTEMA_NOTIFICACOES_FLUTUANTES](features/SISTEMA_NOTIFICACOES_FLUTUANTES.md) | Notificações flutuantes |
| [SOCIAL_NETWORK_GUIDE](features/SOCIAL_NETWORK_GUIDE.md) | Guia da rede social integrada |
| [FRIENDS_LIST_OPTIMIZATION](features/FRIENDS_LIST_OPTIMIZATION.md) | Otimização da lista de amigos |
| [MULTI_ACCOUNT_MANAGEMENT](features/MULTI_ACCOUNT_MANAGEMENT.md) | Gerenciamento de múltiplas contas |
| [LICENSE_SYSTEM](features/LICENSE_SYSTEM.md) | Sistema de licenciamento |
| [PDL_LICENSING_SYSTEM_1.10.0](features/PDL_LICENSING_SYSTEM_1.10.0.md) | Licenciamento v1.10.0 |
| [BANNER_CONFIGURATION](features/BANNER_CONFIGURATION.md) | Configuração de banners |
| [SHOW_PLAYERS_ONLINE_CONFIG](features/SHOW_PLAYERS_ONLINE_CONFIG.md) | Exibição de jogadores online |
| [GRANDBOSS_TIME_CONFIG](features/GRANDBOSS_TIME_CONFIG.md) | Configuração de horários de Grand Boss |
| [DOWNLOADS_INTERNOS](features/DOWNLOADS_INTERNOS.md) | Sistema de downloads internos |
| [GUIA_USUARIO_FINANCEIRO](features/GUIA_USUARIO_FINANCEIRO.md) | Guia financeiro para usuários |
| [DISCORD_BOT_INTEGRATION](features/DISCORD_BOT_INTEGRATION.md) | Integração com bot Discord |
| [SOLICITATION_IMPROVEMENTS](features/SOLICITATION_IMPROVEMENTS.md) | Melhorias no sistema de solicitações |
| [TOPS_TABLES_IMPROVEMENTS](features/TOPS_TABLES_IMPROVEMENTS.md) | Melhorias nas tabelas de tops |
| [AI_ASSISTANT_IMPLEMENTATION](features/AI_ASSISTANT_IMPLEMENTATION.md) | Implementação do assistente de IA |

---

## 🎮 Minigames
> Jogos integrados ao painel.

| Documento | Descrição |
|-----------|-----------|
| [NEW_GAMES_IMPLEMENTATION](games/NEW_GAMES_IMPLEMENTATION.md) | Implementação de novos minigames |
| [COMO_USAR_NOVOS_JOGOS](games/COMO_USAR_NOVOS_JOGOS.md) | Como usar os minigames |

---

## 🔒 Segurança e Autenticação
> Login, CAPTCHA, OAuth e modelo de segurança.

| Documento | Descrição |
|-----------|-----------|
| [DJANGO_L2_SECURITY_MODEL](security/DJANGO_L2_SECURITY_MODEL.md) | Modelo de segurança Django + Lineage 2 |
| [CAPTCHA_LOGIN_SYSTEM](security/CAPTCHA_LOGIN_SYSTEM.md) | Sistema de CAPTCHA no login |
| [SOCIAL_LOGIN_CONFIG](security/SOCIAL_LOGIN_CONFIG.md) | Configuração de login social |
| [SOCIAL_LOGIN_IMPLEMENTATION](security/SOCIAL_LOGIN_IMPLEMENTATION.md) | Implementação do login social |
| [SOCIAL_LOGIN_SUMMARY](security/SOCIAL_LOGIN_SUMMARY.md) | Resumo do login social |

---

## 🔗 Integração com Lineage 2
> Integração com servidor L2, migrações e filtros.

| Documento | Descrição |
|-----------|-----------|
| [LINEAGE_SERVER_INTEGRATION](integration/LINEAGE_SERVER_INTEGRATION.md) | Integração com servidor Lineage 2 |
| [MIGRATION_L2_TO_PDL](integration/MIGRATION_L2_TO_PDL.md) | Migração de dados L2 para o PDL |
| [README_MIGRATION](integration/README_MIGRATION.md) | README de migrações |
| [FILTROS_RETROATIVOS](integration/FILTROS_RETROATIVOS.md) | Filtros retroativos de dados |

---

## 🖼️ Mídia e Armazenamento
> Gerenciamento de arquivos, imagens e armazenamento em nuvem.

| Documento | Descrição |
|-----------|-----------|
| [README_MEDIA_APP](media/README_MEDIA_APP.md) | README do app de mídia |
| [README_S3](media/README_S3.md) | Integração com AWS S3 |
| [COMANDOS_LIMPEZA_MIDIA](media/COMANDOS_LIMPEZA_MIDIA.md) | Comandos de limpeza de mídia |

---

## 🔔 Notificações
> Sistema de notificações e news.

| Documento | Descrição |
|-----------|-----------|
| [README_NOTIFICACOES](notifications/README_NOTIFICACOES.md) | Sistema de notificações |
| [POST_1.14.5_NOTICIAS](notifications/POST_1.14.5_NOTICIAS.md) | Notícias pós-versão 1.14.5 |

---

## 🏆 Rankings (Tops)
> Tabelas de ranking e tops de jogadores.

| Documento | Descrição |
|-----------|-----------|
| [README_TOPS](tops/README_TOPS.md) | Sistema de tops e rankings |

---

## 🛡️ Moderação
> Ferramentas de moderação e exportação de logs.

| Documento | Descrição |
|-----------|-----------|
| [EXPORT_LOGS_MODERACAO](moderation/EXPORT_LOGS_MODERACAO.md) | Exportação de logs de moderação |
| [COMO_TESTAR_MODERACAO](moderation/COMO_TESTAR_MODERACAO.md) | Como testar o sistema de moderação |

---

## 🛠️ Administração Django
> Comandos customizados e ferramentas administrativas.

| Documento | Descrição |
|-----------|-----------|
| [COMANDOS_CUSTOMIZADOS](admin/COMANDOS_CUSTOMIZADOS.md) | Comandos customizados do Django |
| [DOCUMENTACAO_GERADOR_QUERY](admin/DOCUMENTACAO_GERADOR_QUERY.md) | Gerador de queries SQL |

---

## 📊 Observabilidade
> Logging, telemetria e monitoramento.

| Documento | Descrição |
|-----------|-----------|
| [LOGGING](observability/LOGGING.md) | Sistema de logging |
| [TELEMETRY](observability/TELEMETRY.md) | Telemetria e métricas |

---

## 📱 PWA (Progressive Web App)
> Análise e planejamento da versão PWA.

| Documento | Descrição |
|-----------|-----------|
| [ANALISE_TECNICA_PWA](pwa/ANALISE_TECNICA_PWA.md) | Análise técnica da PWA |
| [RESUMO_EXECUTIVO_PWA](pwa/RESUMO_EXECUTIVO_PWA.md) | Resumo executivo da PWA |

---

## 📦 Releases e Changelogs
> Histórico de versões e changelogs.

| Documento | Descrição |
|-----------|-----------|
| [CHANGELOG_2026_02](releases/CHANGELOG_2026_02.md) | Changelog de fevereiro de 2026 |
| [RELEASE_1.11.0_MATRIZ_FILIAL](releases/RELEASE_1.11.0_MATRIZ_FILIAL.md) | Release Matriz/Filial v1.11.0 |
| [RELEASE_1.14.5_RESTRUTURACAO_VISUAL](releases/RELEASE_1.14.5_RESTRUTURACAO_VISUAL.md) | Release Reestruturação Visual v1.14.5 |
| [RELEASE_1.16.0_CONTAS_VINCULADAS](releases/RELEASE_1.16.0_CONTAS_VINCULADAS.md) | Release Contas Vinculadas v1.16.0 |

---

## 🔧 Troubleshooting
> Diagnóstico e resolução de problemas.

| Documento | Descrição |
|-----------|-----------|
| [TROUBLESHOOTING_BUTTONS](troubleshooting/TROUBLESHOOTING_BUTTONS.md) | Diagnóstico de problemas com botões |

---

## 📝 Artigos
> Materiais educativos e artigos técnicos.

| Documento | Descrição |
|-----------|-----------|
| [ARTIGO_IA_PDL](articles/ARTIGO_IA_PDL.md) | Artigo sobre IA no PDL |

---

> 💡 **Dica:** Todos os documentos são gerados a partir do código-fonte e atualizados a cada release.
