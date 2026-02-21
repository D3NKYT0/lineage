# 📚 Wiki do Servidor — Guia do Administrador

> **Última atualização:** 21/02/2026

A **Wiki** do PDL permite criar páginas de conteúdo público para os jogadores do seu servidor: guias de classes, dungeons, regras, FAQs avançados e atualizações do servidor (patch notes).

A Wiki é pública (sem login), acessível em `/public/wiki/` e integra o sistema de temas do PDL.

---

## 1. Estrutura da Wiki

A Wiki possui dois tipos de conteúdo principais:

| Tipo | O que é |
|------|---------|
| **WikiPage** | Páginas com informações permanentes (guias, regras, etc.) |
| **WikiUpdate** | Atualizações do servidor (patch notes com versão e data) |

---

## 2. Gerenciando Páginas (WikiPage)

### Acessando o Painel de Admin
1. Acesse `/admin/` com sua conta de staff.
2. Vá em **Wiki → Wiki Pages**.
3. Clique em **"Add Wiki Page"** para criar uma nova página.

### Campos da Página
| Campo | Descrição |
|-------|-----------|
| **Slug** | URL amigável da página (ex: `guia-de-classes`) |
| **Content Type** | Categoria da página (ver tipos abaixo) |
| **Is Active** | Marque para publicar a página publicamente |
| **Order** | Ordem de exibição no menu da Wiki |

### Tipos de Conteúdo Disponíveis (content_type)
```
guide        – Guias e tutoriais
class        – Classes do jogo
dungeon      – Masmorras e instâncias
boss         – Bosses e raids
system       – Sistemas do servidor
rule         – Regras e políticas
faq          – Perguntas frequentes
other        – Conteúdo geral
```

### Adicionando Traduções (i18n)
A Wiki suporta **múltiplos idiomas**. Para cada página, adicione traduções em:
- **Wiki Page Translations** (vinculadas à `WikiPage`)
- Defina o campo `language` (ex: `pt-br`, `en`) e os campos `title` e `content`.

Apenas a tradução do idioma ativo do usuário é exibida.

---

## 3. Gerenciando Atualizações do Servidor (WikiUpdate)

### Criando uma Atualização
1. No admin, vá em **Wiki → Wiki Updates**.
2. Clique em **"Add Wiki Update"**.
3. Preencha:
   - **Version:** Versão do servidor (ex: `1.5.3`)
   - **Release Date:** Data do patch
   - **Is Active:** Marque para publicar

4. Adicione traduções em **Wiki Update Translations** com título e conteúdo em cada idioma.

### Visualização Pública
- Lista de todas as atualizações: `/public/wiki/updates/`
- Detalhe de uma atualização: `/public/wiki/updates/<id>/`

---

## 4. URLs Públicas da Wiki

| URL | Conteúdo |
|-----|---------|
| `/public/wiki/` | Home da Wiki com pages e últimas 5 atualizações |
| `/public/wiki/updates/` | Todas as atualizações do servidor |
| `/public/wiki/updates/<id>/` | Detalhes de uma atualização |
| `/public/wiki/search/?q=...` | Busca em pages e updates |
| `/public/wiki/sitemap/` | Mapa completo de todas as páginas por categoria |
| `/public/wiki/type/<content_type>/` | Filtra por tipo de conteúdo |
| `/public/wiki/<slug>/` | Página individual |

---

## 5. Temas

A Wiki é integrada com o sistema de temas do PDL. Os templates da Wiki são carregados da pasta do tema ativo. Consulte o [Guia de Temas](../themes/THEME_DEVELOPER_GUIDE.md) para personalizar a aparência da Wiki.

---

## Documentação Relacionada

- 🗺️ [Guia do Roadmap](ROADMAP_ADMIN_GUIDE.md)
- 📰 [Gerenciar Notícias](NEWS_ADMIN_GUIDE.md)

---

[ Voltar ao Índice](../INDEX.md)

