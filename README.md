<div align="center">

# Painel Definitivo Lineage

### A plataforma completa para gerenciar servidores privados de Lineage 2

[![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2+-green?logo=django)](https://www.djangoproject.com)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://docker.com)
[![License](https://img.shields.io/badge/License-Proprietária-red)](LICENSE)

<img height="260" src="https://i.imgur.com/gdB0k6o.jpeg" alt="PDL Preview"/>

</div>

---

## O que é o PDL?

O **PDL (Painel Definitivo Lineage)** nasceu com a missão de oferecer ferramentas poderosas para administradores de servidores privados de Lineage 2. Inicialmente focado em análise de riscos e estabilidade, evoluiu para uma **solução completa e open-source** para prospecção, gerenciamento e operação de servidores.

---

## ✨ Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 💰 **Carteira Virtual** | Saldo, bônus, transferências jogo ↔ painel |
| 🛒 **Loja de Itens** | Carrinho, pacotes, cupons de desconto |
| 🏷️ **Leilões** | Leilão de itens entre jogadores em tempo real |
| 🛍️ **Marketplace** | Compra e venda de personagens |
| 📱 **Rede Social** | Feed, posts, reações, hashtags, chat |
| 🎮 **Minigames** | Roleta, caixas, dados, pesca e muito mais |
| 📊 **Relatórios Financeiros** | Fluxo de caixa, saldos, reconciliação |
| 📚 **Wiki do Servidor** | Páginas públicas com suporte a múltiplos idiomas |
| 🗺️ **Roadmap** | Planos públicos de desenvolvimento |
| 📅 **Calendário** | Eventos e campanhas do servidor |
| 🔒 **Segurança** | 2FA, CAPTCHA, login social, auditoria |
| 🤖 **IA Assistant** | Assistente inteligente integrado |
| 🎨 **Sistema de Temas** | Temas instaláveis via ZIP sem restart |
| 🔔 **Notificações** | Push, in-app, e-mail em tempo real |

---

## ⚡ Começar em 3 Comandos

```bash
git clone https://github.com/D3NKYT0/lineage.git
cd lineage
chmod +x install.sh && ./install.sh
```

O script `install.sh` cuida de **tudo automaticamente** — Docker, ambiente, banco de dados e configuração. 🎉

---

## 🛠️ Tecnologias

<div align="center">

| Backend | Infra | Banco de Dados | Integrações |
|---------|-------|----------------|-------------|
| Python 3.14 | Docker + Compose | PostgreSQL | Mercado Pago |
| Django 5.2+ | Nginx | Redis (cache/broker) | Stripe |
| Celery + Beat | Gunicorn | MySQL (Lineage 2) | AWS S3 |
| Django Channels | Daphne (ASGI) | — | Google / Discord OAuth |

</div>

---

## 📚 Documentação

A documentação completa está em [`docs/`](docs/INDEX.md), organizada por tipo de usuário:

| Você é... | Documentação |
|-----------|-------------|
| 🧑 **Jogador / Usuário** | [Guia do Usuário Final](docs/INDEX.md#-guia-do-usuário-final) — Carteira, Loja, Leilão, Social |
| 🛠️ **Dono do Servidor** | [Guia do Administrador](docs/INDEX.md#️-guia-do-administrador) — Pagamentos, Relatórios, Wiki |
| 👩‍💻 **Desenvolvedor** | [Instalação](docs/installation/INSTALLATION_AND_DEPLOY.md) · [API](docs/api/API_DOCUMENTATION.md) · [Temas](docs/themes/THEME_SYSTEM.md) |

---

## 🌐 Demonstração

Acesse o ambiente de demonstração em:
**[https://pdl.denky.dev.br](https://pdl.denky.dev.br)**

---

## 👤 Autor

**Daniel Amaral** — Desenvolvedor FullStack/FullCycle
- 📧 contato@denky.dev.br
- 💬 Discord: `denkyto`
- 🌐 [denky.dev.br](https://denky.dev.br)
