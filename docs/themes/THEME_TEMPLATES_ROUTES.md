# Rotas Suportadas por Temas - PDL

> **Última atualização:** 21/02/2026

Este documento lista todas as rotas que podem ser substituídas por arquivos de tema no sistema PDL (Private Development Lineage).

## 📋 Índice

1. [Páginas Públicas](#paginas-publicas)
2. [Hub Downloads](#hub-downloads)
3. [Hub Tops](#hub-tops)
4. [Hub Wiki](#hub-wiki)
5. [Sistema de Contas](#sistema-contas)
6. [Estrutura de Arquivos do Tema](#estrutura-arquivos)
7. [Como Funciona](#como-funciona)

---

## 🌐 Páginas Públicas {#paginas-publicas}

### Página Inicial
- **Rota**: `/`
- **Template do Tema**: `index.html` *(Consulte as [variáveis de contexto específicas aqui](THEME_INDEX_CONTEXT.md))*
- **Template Padrão**: `public/index.html`

### Páginas Legais
- **Rota**: `/public/terms/`
- **Template do Tema**: `terms.html`
- **Template Padrão**: `public/terms.html`

- **Rota**: `/public/user-agreement/`
- **Template do Tema**: `user_agreement.html`
- **Template Padrão**: `public/user_agreement.html`

- **Rota**: `/public/privacy-policy/`
- **Template do Tema**: `privacy_policy.html`
- **Template Padrão**: `public/privacy_policy.html`

### Sistema de Notícias
- **Rota**: `/public/news/`
- **Template do Tema**: `news_index.html`
- **Template Padrão**: `public/news_index.html`

- **Rota**: `/public/news/<slug>/`
- **Template do Tema**: `news_detail.html`
- **Template Padrão**: `public/news_detail.html`

### FAQ
- **Rota**: `/public/faq/`
- **Template do Tema**: `faq.html`
- **Template Padrão**: `public/faq.html`

### Verificação de Email
- **Rota**: `/verify/<uidb64>/<token>/`
- **Template do Tema**: `email_verificado.html`
- **Template Padrão**: `public/email_verificado.html`

### Páginas de Sistema
- **Rota**: `/public/maintenance/`
- **Template do Tema**: `maintenance.html`
- **Template Padrão**: `public/maintenance_isolated.html`

- **Rota**: `/public/license-expired/`
- **Template do Tema**: `license_expired.html`
- **Template Padrão**: `public/license_expired.html`

---

## 📥 Hub Downloads {#hub-downloads}

### Página Principal
- **Rota**: `/public/downloads/`
- **Template do Tema**: `downloads.html`
- **Template Padrão**: `public/downloads.html`

---

## 🏆 Hub Tops {#hub-tops}

### Página Inicial
- **Rota**: `/public/tops/`
- **Template do Tema**: `home.html`
- **Template Padrão**: `tops/home.html`

### Rankings
- **Rota**: `/public/tops/pvp/`
- **Template do Tema**: `pvp.html`
- **Template Padrão**: `tops/pvp.html`

- **Rota**: `/public/tops/pk/`
- **Template do Tema**: `pk.html`
- **Template Padrão**: `tops/pk.html`

- **Rota**: `/public/tops/adena/`
- **Template do Tema**: `adena.html`
- **Template Padrão**: `tops/adena.html`

- **Rota**: `/public/tops/clans/`
- **Template do Tema**: `clans.html`
- **Template Padrão**: `tops/clans.html`

- **Rota**: `/public/tops/level/`
- **Template do Tema**: `level.html`
- **Template Padrão**: `tops/level.html`

- **Rota**: `/public/tops/online/`
- **Template do Tema**: `online.html`
- **Template Padrão**: `tops/online.html`

- **Rota**: `/public/tops/olympiad/`
- **Template do Tema**: `olympiad.html`
- **Template Padrão**: `tops/olympiad.html`

- **Rota**: `/public/tops/siege/`
- **Template do Tema**: `siege.html`
- **Template Padrão**: `tops/siege.html`

---

## 📚 Hub Wiki {#hub-wiki}

### Página Inicial
- **Rota**: `/public/wiki/`
- **Template do Tema**: `home.html`
- **Template Padrão**: `wiki/home.html`

### Páginas por Tipo
- **Rota**: `/public/wiki/type/<content_type>/`
- **Template do Tema**: `pages.html`
- **Template Padrão**: `wiki/pages.html`

### Página Individual
- **Rota**: `/public/wiki/<slug>/`
- **Template do Tema**: `page_detail.html`
- **Template Padrão**: `wiki/page_detail.html`

### Atualizações
- **Rota**: `/public/wiki/updates/`
- **Template do Tema**: `updates.html`
- **Template Padrão**: `wiki/updates.html`

- **Rota**: `/public/wiki/updates/<int:pk>/`
- **Template do Tema**: `update_detail.html`
- **Template Padrão**: `wiki/update_detail.html`

### Busca
- **Rota**: `/public/wiki/search/`
- **Template do Tema**: `search.html`
- **Template Padrão**: `wiki/search.html`

### Mapa do Site
- **Rota**: `/public/wiki/sitemap/`
- **Template do Tema**: `sitemap.html`
- **Template Padrão**: `wiki/sitemap.html`

---

## 🔐 Sistema de Contas {#sistema-contas}

### Autenticação Principal
- **Rota**: `/accounts/register/`
- **Template do Tema**: `sign-up.html`
- **Template Padrão**: `accounts_custom/sign-up.html`

- **Rota**: `/accounts/login/`
- **Template do Tema**: `sign-in.html`
- **Template Padrão**: `accounts_custom/sign-in.html`

### Alteração de Senha
- **Rota**: `/accounts/password-change/`
- **Template do Tema**: `password-change.html`
- **Template Padrão**: `accounts_custom/password-change.html`

- **Rota**: `/accounts/password-change-done/`
- **Template do Tema**: `password-change-done.html`
- **Template Padrão**: `accounts_custom/password-change-done.html`

### Reset de Senha
- **Rota**: `/accounts/password-reset/`
- **Template do Tema**: `forgot-password.html`
- **Template Padrão**: `accounts_custom/forgot-password.html`

- **Rota**: `/accounts/password-reset-done/`
- **Template do Tema**: `password-reset-done.html`
- **Template Padrão**: `accounts_custom/password-reset-done.html`

- **Rota**: `/accounts/password-reset-confirm/<uidb64>/<token>/`
- **Template do Tema**: `reset-password.html`
- **Template Padrão**: `accounts_custom/reset-password.html`

- **Rota**: `/accounts/password-reset-complete/`
- **Template do Tema**: `password-reset-complete.html`
- **Template Padrão**: `accounts_custom/password-reset-complete.html`

### Sistema de Bloqueio
- **Rota**: `/accounts/lock/`
- **Template do Tema**: `lock.html`
- **Template Padrão**: `accounts_custom/lock.html`

### Registro e Sucesso
- **Rota**: `/accounts/registration/success/`
- **Template do Tema**: `registration_success.html`
- **Template Padrão**: `accounts_custom/registration_success.html`

### Autenticação em Duas Etapas (2FA)
- **Rota**: `/accounts/2fa/`
- **Template do Tema**: `verify-2fa.html`
- **Template Padrão**: `accounts_custom/verify-2fa.html`

- **Rota**: `/accounts/activate-2fa/`
- **Template do Tema**: `ativar-2fa.html`
- **Template Padrão**: `accounts_custom/ativar-2fa.html`

---

## 📁 Estrutura de Arquivos do Tema {#estrutura-arquivos}

Para criar um tema que substitua todas essas rotas, sua estrutura deve ser:

```
meu-tema.zip
├── theme.json                 # OBRIGATÓRIO - Configuração do tema
├── base.html                  # OBRIGATÓRIO - Template base
│
├── # Páginas Públicas
├── index.html                 # Página inicial
├── terms.html                 # Termos de uso
├── user_agreement.html        # Acordo do usuário
├── privacy_policy.html        # Política de privacidade
├── news_index.html            # Lista de notícias
├── news_detail.html           # Detalhe da notícia
├── faq.html                   # FAQ
├── email_verificado.html      # Verificação de email
├── maintenance.html           # Manutenção
├── license_expired.html       # Licença expirada
│
├── # Hub Downloads
├── downloads.html             # Hub de downloads
│
├── # Hub Tops
├── home.html                  # Home dos tops (sobrescreve tops/home.html)
├── pvp.html                   # Ranking PvP
├── pk.html                    # Ranking PK
├── adena.html                 # Ranking Adena
├── clans.html                 # Ranking Clãs
├── level.html                 # Ranking Nível
├── online.html                # Top Online
├── olympiad.html              # Ranking Olimpíada
├── siege.html                 # Castle & Siege
│
├── # Hub Wiki
├── home.html                  # Home do wiki (sobrescreve wiki/home.html)
├── pages.html                 # Páginas por tipo
├── page_detail.html           # Página individual
├── updates.html               # Lista de atualizações
├── update_detail.html         # Detalhe da atualização
├── search.html                # Busca no wiki
├── sitemap.html               # Mapa do site
│
├── # Sistema de Contas
├── sign-up.html               # Registro
├── sign-in.html               # Login
├── password-change.html       # Alterar senha
├── password-change-done.html  # Sucesso alteração
├── forgot-password.html       # Esqueci senha
├── password-reset-done.html   # Sucesso envio reset
├── reset-password.html        # Confirmação reset
├── password-reset-complete.html # Sucesso reset
├── lock.html                  # Bloqueio de tela
├── registration_success.html  # Sucesso registro
├── verify-2fa.html            # Verificação 2FA
├── ativar-2fa.html            # Ativação 2FA
│
├── # Assets (opcional)
├── css/
│   ├── style.css
│   └── main.css
├── js/
│   ├── script.js
│   └── custom.js
├── images/
│   ├── logo.png
│   └── backgrounds/
└── fonts/
    └── custom-fonts.woff2
```

---

## ⚙️ Como Funciona {#como-funciona}

### 1. **Prioridade do Tema**
O sistema primeiro verifica se existe um template correspondente no diretório do tema ativo (`themes/installed/[nome-tema]/`).

### 2. **Fallback Automático**
Se o template não existir no tema, usa automaticamente o template padrão do sistema.

### 3. **Contexto Completo**
Todos os templates do tema recebem o mesmo contexto que os templates padrão, incluindo:
- Variáveis do tema (`theme_slug`, `path_theme`, etc.)
- Variáveis do sistema (`PROJECT_TITLE`, `PROJECT_LOGO_URL`, etc.)
- Contexto específico da página

### 4. **Tratamento de Erros**
Se houver erro no template do tema (sintaxe inválida, URL quebrada, etc.):
- O sistema registra o erro nos logs
- Automaticamente usa o template padrão como fallback
- Opcionalmente exibe mensagem de erro para o usuário (configurável)

### 5. **Compatibilidade**
- ✅ Mantém total compatibilidade com o sistema existente
- ✅ Não quebra funcionalidades existentes
- ✅ Permite personalização granular (você pode substituir apenas alguns templates)
- ✅ Suporte completo a internacionalização (i18n)

---

## 📝 Notas Importantes

### Templates Obrigatórios
- `theme.json` - Metadados do tema
- `base.html` - Template base (usado por todos os outros templates)

### Templates Opcionais
Todos os outros templates são opcionais. Se não existirem no tema, o sistema usará os templates padrão.

### Conflitos de Nome
Alguns templates têm nomes similares (ex: `home.html` para tops e wiki). O sistema resolve isso usando o caminho correto baseado na rota acessada.

### Desenvolvimento
Para desenvolver temas, consulte:
- `docs/THEME_DEVELOPER_GUIDE.md` - Guia completo para desenvolvedores
- `../themes/GUIDE_CREATE_THEME.md` - Como criar temas
- `../themes/THEME_SYSTEM.md` - Visão geral do sistema de temas

---

## 🔄 Atualizações

Este documento será atualizado sempre que novas rotas forem adicionadas ao sistema de temas.

**Última atualização**: Dezembro 2024
**Versão**: 1.0

---

[ Voltar ao Índice](../INDEX.md)

