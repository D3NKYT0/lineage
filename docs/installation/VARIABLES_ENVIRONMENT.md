# Variáveis de Ambiente - Lineage 2 PDL

Este documento lista todas as variáveis de ambiente possíveis utilizadas no projeto Lineage 2 PDL.

## 📋 Índice

- [Configurações Básicas](#configurações-básicas)
- [Banco de Dados](#banco-de-dados)
- [Banco de Dados Lineage](#banco-de-dados-lineage)
- [AWS S3](#aws-s3)
- [Email](#email)
- [Cache e Redis](#cache-e-redis)
- [Celery](#celery)
- [Channels](#channels)
- [Autenticação Social](#autenticação-social)
- [Pagamentos](#pagamentos)
- [Captcha](#captcha)
- [Configurações do Projeto](#configurações-do-projeto)
- [Configurações de Internacionalização](#configurações-de-internacionalização)
- [Status do Servidor](#status-do-servidor)
- [Jogadores Falsos](#jogadores-falsos)
- [Licença](#licença)
- [Web Push](#web-push)
- [Outras Configurações](#outras-configurações)

---

## 🔧 Configurações Básicas

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `DEBUG` | Boolean | `False` | Habilita/desabilita o modo debug |
| `SECRET_KEY` | String | - | Chave secreta do Django (obrigatória) |
| `GUNICORN_WORKERS` | Integer | `4` ou `(CPU*2)+1` | Número de workers do Gunicorn (afeta conexões de banco) |
| `RUNNING_IN_DOCKER` | Boolean | `false` | Indica se está rodando em container Docker |
| `RENDER_EXTERNAL_HOSTNAME` | String | - | Hostname externo do Render |
| `RENDER_EXTERNAL_FRONTEND` | String | - | Frontend externo do Render |

---

## 🗄️ Banco de Dados

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `DB_ENGINE` | String | - | Engine do banco (postgresql, mysql, sqlite3) |
| `DB_HOST` | String | `localhost` | Host do banco de dados |
| `DB_NAME` | String | - | Nome do banco de dados |
| `DB_USERNAME` | String | - | Usuário do banco de dados |
| `DB_PASS` | String | - | Senha do banco de dados |
| `DB_PORT` | String | - | Porta do banco de dados |

---

## 🎮 Banco de Dados Lineage

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `LINEAGE_DB_ENABLED` | Boolean | `false` | Habilita conexão com banco do Lineage |
| `LINEAGE_DB_NAME` | String | - | Nome do banco do Lineage |
| `LINEAGE_DB_USER` | String | - | Usuário do banco do Lineage |
| `LINEAGE_DB_PASSWORD` | String | - | Senha do banco do Lineage |
| `LINEAGE_DB_HOST` | String | - | Host do banco do Lineage |
| `LINEAGE_DB_PORT` | String | `3306` | Porta do banco do Lineage |
| `LINEAGE_DB_POOL_SIZE` | Integer | `1` | Número de conexões permanentes no pool por worker |
| `LINEAGE_DB_MAX_OVERFLOW` | Integer | `2` | Número máximo de conexões extras além do pool_size |
| `LINEAGE_QUERY_MODULE` | String | `dreamv3` | Módulo de queries do Lineage |

---

## ☁️ AWS S3

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `USE_S3` | Boolean | `False` | Habilita uso do AWS S3 |
| `AWS_ACCESS_KEY_ID` | String | - | Access Key ID da AWS |
| `AWS_SECRET_ACCESS_KEY` | String | - | Secret Access Key da AWS |
| `AWS_STORAGE_BUCKET_NAME` | String | - | Nome do bucket S3 |
| `AWS_S3_REGION_NAME` | String | `us-east-1` | Região do S3 |
| `AWS_S3_CUSTOM_DOMAIN` | String | - | Domínio customizado do S3 |

---

## 📧 Email

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CONFIG_EMAIL_ENABLE` | Boolean | `False` | Habilita envio de emails |
| `CONFIG_EMAIL_USE_TLS` | Boolean | `True` | Usa TLS para conexão SMTP |
| `CONFIG_EMAIL_HOST` | String | - | Servidor SMTP |
| `CONFIG_EMAIL_HOST_USER` | String | - | Usuário do email |
| `CONFIG_EMAIL_HOST_PASSWORD` | String | - | Senha do email |
| `CONFIG_EMAIL_PORT` | Integer | `587` | Porta do servidor SMTP |
| `CONFIG_DEFAULT_FROM_EMAIL` | String | - | Email remetente padrão |
| `ACCOUNT_EMAIL_VERIFICATION` | String | `none` | Verificação de email (none, mandatory, optional) |

---

## 🚀 Cache e Redis

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `DJANGO_CACHE_REDIS_URI` | String | - | URI do Redis para cache |
| `CHANNELS_BACKEND` | String | `redis://redis:6379/2` | Backend do Channels (Redis) |

---

## 🔄 Celery

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CELERY_BROKER_URI` | String | `redis://redis:6379/1` | URI do broker do Celery |
| `CELERY_BACKEND_URI` | String | `redis://redis:6379/1` | URI do backend do Celery |

---

## 🔐 Autenticação Social

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `SOCIAL_LOGIN_ENABLED` | Boolean | `False` | Habilita login social globalmente |
| `SOCIAL_LOGIN_GOOGLE_ENABLED` | Boolean | `False` | Habilita login com Google |
| `SOCIAL_LOGIN_GITHUB_ENABLED` | Boolean | `False` | Habilita login com GitHub |
| `SOCIAL_LOGIN_DISCORD_ENABLED` | Boolean | `False` | Habilita login com Discord |
| `SOCIAL_LOGIN_SHOW_SECTION` | Boolean | `False` | Mostra seção de login social |
| `GOOGLE_CLIENT_ID` | String | - | Client ID do Google OAuth |
| `GOOGLE_SECRET_KEY` | String | - | Secret Key do Google OAuth |
| `GITHUB_CLINET_ID` | String | - | Client ID do GitHub OAuth |
| `GITHUB_SECRET_KEY` | String | - | Secret Key do GitHub OAuth |
| `DISCORD_CLIENT_ID` | String | - | Client ID do Discord OAuth |
| `DISCORD_SECRET_KEY` | String | - | Secret Key do Discord OAuth |

---

## 💳 Pagamentos

### Mercado Pago
| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CONFIG_MERCADO_PAGO_ACCESS_TOKEN` | String | - | Access Token do Mercado Pago |
| `CONFIG_MERCADO_PAGO_PUBLIC_KEY` | String | - | Public Key do Mercado Pago |
| `CONFIG_MERCADO_PAGO_CLIENT_ID` | String | - | Client ID do Mercado Pago |
| `CONFIG_MERCADO_PAGO_CLIENT_SECRET` | String | - | Client Secret do Mercado Pago |
| `CONFIG_MERCADO_PAGO_SIGNATURE` | String | - | Assinatura do webhook do Mercado Pago |
| `CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS` | Boolean | - | Ativa pagamentos via Mercado Pago |

### Stripe
| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CONFIG_STRIPE_WEBHOOK_SECRET` | String | - | Secret do webhook do Stripe |
| `CONFIG_STRIPE_SECRET_KEY` | String | - | Secret Key do Stripe |
| `CONFIG_STRIPE_ACTIVATE_PAYMENTS` | Boolean | - | Ativa pagamentos via Stripe |

---

## 🤖 Captcha

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CONFIG_HCAPTCHA_SITE_KEY` | String | - | Site Key do hCaptcha |
| `CONFIG_HCAPTCHA_SECRET_KEY` | String | - | Secret Key do hCaptcha |
| `CONFIG_LOGIN_MAX_ATTEMPTS` | Integer | `3` | Máximo de tentativas de login antes do captcha |

---

## 🎨 Configurações do Projeto

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `PROJECT_TITLE` | String | `Lineage 2 PDL` | Título do projeto |
| `PROJECT_AUTHOR` | String | `Lineage 2 PDL` | Autor do projeto |
| `PROJECT_DESCRIPTION` | String | - | Descrição do projeto |
| `PROJECT_KEYWORDS` | String | `lineage l2 painel servidor` | Palavras-chave do projeto |
| `PROJECT_URL` | String | `#` | URL do projeto |
| `PROJECT_LOGO_URL` | String | `/static/assets/img/logo_painel.png` | URL do logo |
| `PROJECT_FAVICON_ICO` | String | `/static/assets/img/ico.jpg` | URL do favicon |
| `PROJECT_FAVICON_MANIFEST` | String | `/static/assets/img/favicon/site.webmanifest` | URL do manifest |
| `PROJECT_THEME_COLOR` | String | `#ffffff` | Cor do tema |
| `PROJECT_DISCORD_URL` | String | - | URL do Discord |
| `PROJECT_YOUTUBE_URL` | String | - | URL do YouTube |
| `PROJECT_FACEBOOK_URL` | String | - | URL do Facebook |
| `PROJECT_INSTAGRAM_URL` | String | - | URL do Instagram |
| `SLOGAN` | Boolean | `True` | Habilita exibição do slogan |

---

## 🌍 Configurações de Internacionalização

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CONFIG_LANGUAGE_CODE` | String | `pt` | Código do idioma |
| `CONFIG_TIME_ZONE` | String | `America/Recife` | Fuso horário |
| `CONFIG_DECIMAL_SEPARATOR` | String | `,` | Separador decimal |
| `CONFIG_USE_THOUSAND_SEPARATOR` | Boolean | `True` | Usa separador de milhares |
| `CONFIG_DATETIME_FORMAT` | String | `d/m/Y H:i:s` | Formato de data/hora |
| `CONFIG_DATE_FORMAT` | String | `d/m/Y` | Formato de data |
| `CONFIG_TIME_FORMAT` | String | `H:i:s` | Formato de hora |
| `CONFIG_GMT_OFFSET` | Float | `-3` | Offset GMT |
| `CONFIG_GRANDBOSS_SHOW_TIME` | Boolean | `True` | Mostra hora nos Grand Bosses |
| `CONFIG_SHOW_PLAYERS_ONLINE` | Boolean | `True` | Mostra jogadores online |

---

## 🎮 Status do Servidor

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `GAME_SERVER_IP` | String | `127.0.0.1` | IP do servidor de jogo |
| `GAME_SERVER_PORT` | Integer | `7777` | Porta do servidor de jogo |
| `LOGIN_SERVER_PORT` | Integer | `2106` | Porta do servidor de login |
| `SERVER_STATUS_TIMEOUT` | Integer | `1` | Timeout para verificação de status |
| `FORCE_GAME_SERVER_STATUS` | String | `auto` | Força status do servidor de jogo |
| `FORCE_LOGIN_SERVER_STATUS` | String | `auto` | Força status do servidor de login |

---

## 👥 Jogadores Falsos

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `FAKE_PLAYERS_FACTOR` | Float | `1.0` | Multiplicador de jogadores online |
| `FAKE_PLAYERS_MIN` | Integer | `0` | Mínimo de jogadores online |
| `FAKE_PLAYERS_MAX` | Integer | `0` | Máximo de jogadores online |

---

## 📜 Licença

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `PDL_ENCRYPTION_KEY` | String | - | Chave de criptografia para licenças |
| `PDL_DNS_TIMEOUT` | Integer | `10` | Timeout DNS para validação de licença |

---

## 🔔 Web Push

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `VAPID_PRIVATE_KEY` | String | - | Chave privada VAPID |
| `VAPID_PUBLIC_KEY` | String | - | Chave pública VAPID |

---

## 🔒 Segurança e Criptografia

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `ENCRYPTION_KEY` | String | - | Chave de criptografia geral |
| `DATA_UPLOAD_MAX_MEMORY_SIZE` | Integer | `57671680` | Tamanho máximo de upload |
| `SERVE_DECRYPTED_FILE_URL_BASE` | String | `decrypted-file` | Base URL para arquivos descriptografados |

---

## 🔍 Auditoria

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `CONFIG_AUDITOR_MIDDLEWARE_ENABLE` | Boolean | `False` | Habilita middleware de auditoria |
| `CONFIG_AUDITOR_MIDDLEWARE_RESTRICT_PATHS` | List | - | Caminhos restritos para auditoria |

---

## 🎬 Processamento de Mídia

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `FFMPEG_PATH` | String | `ffmpeg` | Caminho para o executável ffmpeg |
| `FFPROBE_PATH` | String | `ffprobe` | Caminho para o executável ffprobe |

---

## 🛡️ Proteção contra Spam

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `DISABLE_SPAM_PROTECTION` | Boolean | `False` | Desabilita proteção contra spam |

---

## 🤖 Assistente de IA

| Variável | Tipo | Padrão | Descrição |
|----------|------|--------|-----------|
| `ANTHROPIC_API_KEY` | String | - | Chave da API da Anthropic (Claude) |
| `GEMINI_API_KEY` | String | - | Chave da API do Google Gemini |
| `XAI_API_KEY` | String | - | Chave da API do xAI (Grok) |

**Nota**: O provedor de IA pode ser escolhido no admin através do modelo `AIProviderConfig`. Apenas uma configuração pode estar ativa por vez. Opções disponíveis: Anthropic (Claude), Google Gemini ou xAI Grok.

---

## 📝 Exemplo de Arquivo .env

```bash
# =========================== CONFIGURAÇÕES BÁSICAS ===========================
DEBUG=False
SECRET_KEY=sua_chave_secreta_aqui
RUNNING_IN_DOCKER=True
RENDER_EXTERNAL_HOSTNAME=seu-dominio.com
RENDER_EXTERNAL_FRONTEND=seu-dominio.com

# =========================== BANCO DE DADOS ===========================
DB_ENGINE=postgresql
DB_HOST=postgres
DB_NAME=db_name
DB_USERNAME=db_user
DB_PASS=db_pass
DB_PORT=5432

# =========================== BANCO DE DADOS LINEAGE ===========================
LINEAGE_DB_ENABLED=True
LINEAGE_DB_NAME=l2jdb
LINEAGE_DB_USER=l2user
LINEAGE_DB_PASSWORD=suaSenhaAqui
LINEAGE_DB_HOST=192.168.1.100
LINEAGE_DB_PORT=3306
LINEAGE_DB_POOL_SIZE=2
LINEAGE_DB_MAX_OVERFLOW=3
LINEAGE_QUERY_MODULE=dreamv3

# =========================== AWS S3 ===========================
USE_S3=False
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
AWS_S3_CUSTOM_DOMAIN=your-bucket-name.s3.amazonaws.com

# =========================== EMAIL ===========================
CONFIG_EMAIL_ENABLE=False
CONFIG_EMAIL_USE_TLS=True
CONFIG_EMAIL_HOST=smtp.domain.com
CONFIG_EMAIL_HOST_USER=mail@mail.dev.br
CONFIG_DEFAULT_FROM_EMAIL=mail@mail.dev.br
CONFIG_EMAIL_HOST_PASSWORD=password
CONFIG_EMAIL_PORT=587

# =========================== CACHE E REDIS ===========================
CONFIG_AUDITOR_MIDDLEWARE_ENABLE=True
DJANGO_CACHE_REDIS_URI=redis://redis:6379/0
CELERY_BROKER_URI=redis://redis:6379/1
CELERY_BACKEND_URI=redis://redis:6379/1
CHANNELS_BACKEND=redis://redis:6379/2

# =========================== CRIPTOGRAFIA ===========================
ENCRYPTION_KEY=iOg0mMfE54rqvAOZKxhmb-Rq0sgmRC4p1TBGu_JqHac=
DATA_UPLOAD_MAX_MEMORY_SIZE=31457280

# =========================== PAGAMENTOS ===========================
CONFIG_MERCADO_PAGO_ACCESS_TOKEN=APP_USR-0000000000000000-000000-00000000000000000000000000000000-000000000
CONFIG_MERCADO_PAGO_PUBLIC_KEY=APP_USR-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
CONFIG_MERCADO_PAGO_CLIENT_ID=0000000000000000
CONFIG_MERCADO_PAGO_CLIENT_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CONFIG_MERCADO_PAGO_SIGNATURE=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
CONFIG_MERCADO_PAGO_ACTIVATE_PAYMENTS=True

CONFIG_STRIPE_WEBHOOK_SECRET=whsec_5dzjceF7LgeYzasdasdasdZpSuPq
CONFIG_STRIPE_SECRET_KEY=sk_test_51RK0cORmyaPSbmPDEMjN0DaasdasdadadasdafgagdhhfasdfsfnbgRrtdKRwHRakfrQub9SQ5jQEUNvTfrcFxbw00gsqFR09W
CONFIG_STRIPE_ACTIVATE_PAYMENTS=True

# =========================== CAPTCHA ===========================
CONFIG_HCAPTCHA_SITE_KEY=bcf40348-fa88-4570-a752-2asdasde0b2bc
CONFIG_HCAPTCHA_SECRET_KEY=ES_dc688fdasdasdadasdas4e918093asddsddsafa3f1b
CONFIG_LOGIN_MAX_ATTEMPTS=3

# =========================== CONFIGURAÇÕES DO PROJETO ===========================
PROJECT_TITLE=Lineage 2 PDL
PROJECT_AUTHOR=Lineage 2 PDL
PROJECT_DESCRIPTION=O PDL é um painel que nasceu com a missão de oferecer ferramentas poderosas para administradores de servidores privados de Lineage 2.
PROJECT_KEYWORDS=lineage l2 painel servidor
PROJECT_URL=https://pdl.denky.dev.br
PROJECT_LOGO_URL=/static/assets/img/logo_painel.png
PROJECT_FAVICON_ICO=/static/assets/img/ico.jpg
PROJECT_FAVICON_MANIFEST=/static/assets/img/favicon/site.webmanifest
PROJECT_THEME_COLOR=#ffffff

PROJECT_DISCORD_URL=https://discord.gg/seu-link-aqui
PROJECT_YOUTUBE_URL=https://www.youtube.com/@seu-canal
PROJECT_FACEBOOK_URL=https://www.facebook.com/sua-pagina
PROJECT_INSTAGRAM_URL=https://www.instagram.com/seu-perfil

SLOGAN=True

# =========================== AUTENTICAÇÃO SOCIAL ===========================
GOOGLE_CLIENT_ID=3029asdasd17179-i4lfm6078nrov5lhv9628bch2o8vlqs8.apps.googleusercontent.com
GOOGLE_SECRET_KEY=GOCSPX-bWw9hU6Mb3pasdasdasd

GITHUB_CLINET_ID=Ov23liadadadwcXpjog38V
GITHUB_SECRET_KEY=ea0d1c77b910eadadadada65a7cbddee1bd07deb

DISCORD_CLIENT_ID=13836455adada77550336
DISCORD_SECRET_KEY=Gs9db5OmQ9dadadadadad8CtOQuLKx42fdf

SOCIAL_LOGIN_ENABLED=False
SOCIAL_LOGIN_GOOGLE_ENABLED=False
SOCIAL_LOGIN_GITHUB_ENABLED=False
SOCIAL_LOGIN_DISCORD_ENABLED=False
SOCIAL_LOGIN_SHOW_SECTION=False

# =========================== INTERNACIONALIZAÇÃO ===========================
CONFIG_LANGUAGE_CODE=pt
CONFIG_TIME_ZONE=America/Recife
CONFIG_DECIMAL_SEPARATOR=,
CONFIG_USE_THOUSAND_SEPARATOR=True
CONFIG_DATETIME_FORMAT=d/m/Y H:i:s
CONFIG_DATE_FORMAT=d/m/Y
CONFIG_TIME_FORMAT=H:i:s
CONFIG_GMT_OFFSET=-3
CONFIG_GRANDBOSS_SHOW_TIME=True
CONFIG_SHOW_PLAYERS_ONLINE=True

# =========================== STATUS DO SERVIDOR ===========================
GAME_SERVER_IP=192.168.1.100
GAME_SERVER_PORT=7777
LOGIN_SERVER_PORT=2106
SERVER_STATUS_TIMEOUT=1
FORCE_GAME_SERVER_STATUS=auto
FORCE_LOGIN_SERVER_STATUS=auto

# =========================== JOGADORES FALSOS ===========================
FAKE_PLAYERS_FACTOR=1.0
FAKE_PLAYERS_MIN=0
FAKE_PLAYERS_MAX=0

# =========================== LICENÇA ===========================
PDL_ENCRYPTION_KEY=
PDL_DNS_TIMEOUT=10

# =========================== WEB PUSH ===========================
VAPID_PRIVATE_KEY=
VAPID_PUBLIC_KEY=

# =========================== PROCESSAMENTO DE MÍDIA ===========================
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe

# =========================== PROTEÇÃO CONTRA SPAM ===========================
DISABLE_SPAM_PROTECTION=False
```

---

## ⚠️ Notas Importantes

1. **Variáveis Obrigatórias**: Algumas variáveis são obrigatórias e o sistema não funcionará sem elas:
   - `SECRET_KEY`
   - `ENCRYPTION_KEY`
   - `CONFIG_HCAPTCHA_SITE_KEY`
   - `CONFIG_HCAPTCHA_SECRET_KEY`

2. **Variáveis de Pagamento**: Se você ativar pagamentos, certifique-se de configurar todas as variáveis relacionadas ao método escolhido.

3. **Banco de Dados**: Configure pelo menos uma das opções de banco de dados (principal ou Lineage).

4. **Redis**: Para funcionalidades avançadas como cache, Celery e Channels, o Redis é necessário.

5. **Docker**: Se estiver usando Docker, certifique-se de que `RUNNING_IN_DOCKER=True`.

---

## 🔧 Como Usar

1. Copie o arquivo `env.sample` para `.env`
2. Configure as variáveis conforme suas necessidades
3. Reinicie o servidor para aplicar as mudanças

```bash
cp env.sample .env
# Edite o arquivo .env com suas configurações
python manage.py runserver
```
