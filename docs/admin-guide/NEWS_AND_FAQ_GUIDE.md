# 📰 Gerenciando Notícias e FAQ — Guia do Administrador

> **Última atualização:** 21/02/2026

O PDL possui módulos de **Notícias** e **FAQ** para comunicar informações importantes e responder dúvidas recorrentes dos jogadores.

---

## 1. Sistema de Notícias

### Acesso
Gerencie notícias via painel Django Admin: `/admin/news/`.

### Publicando uma Notícia
1. Acesse **Admin → News → Posts → Add Post**.
2. Preencha:
   - **Título:** Título da notícia
   - **Slug:** URL única da notícia (gerada automaticamente)  
   - **Conteúdo:** Corpo da notícia (suporte a HTML/Rich Text)
   - **Imagem de Capa:** Imagem de destaque (opcional)
   - **Publicado:** Marque para tornar público

3. Salve para publicar.

### URLs Públicas
| URL | Conteúdo |
|-----|---------|
| `/app/news/` | Lista de todas as notícias |
| `/app/news/<slug>/` | Detalhe de uma notícia |

---

## 2. Sistema de FAQ

O FAQ exibe perguntas e respostas organizadas para os jogadores.

### Acesso
Gerencie no Django Admin: `/admin/faq/`.

### Adicionando uma Pergunta
1. Acesse **Admin → Faq → Questions → Add Question**.
2. Preencha:
   - **Pergunta:** O texto da dúvida
   - **Resposta:** A explicação (suporte a HTML)
   - **Categoria:** Agrupe por tema (ex: Pagamentos, Conta, Itens)
   - **Ativo:** Marque para exibir na lista pública
   - **Ordem:** Número para controlar a sequência de exibição

3. Salve.

### URL Pública
| URL | Conteúdo |
|-----|---------|
| `/app/faq/` | Lista todas as perguntas ativas, agrupadas por categoria |

---

## 3. Boas Práticas

### Para Notícias
- Escreva títulos claros e diretos.
- Use imagens de capa — elas aumentam o engajamento.
- Publique notícias sobre eventos, promoções e manutenções com antecedência.
- Use slugs descritivos (ex: `evento-natal-2026` em vez de `post-1`).

### Para FAQ
- Mantenha as respostas concisas — se ficou longa, transforme em notícia ou wiki.
- Agrupe por categorias para facilitar a navegação.
- Revise regularmente e remova perguntas desatualizadas (`Ativo = False`).

---

## Documentação Relacionada

- 📚 [Wiki do Servidor](WIKI_ADMIN_GUIDE.md)
- 📅 [Calendário de Eventos](CALENDARY_GUIDE.md)

---

[ Voltar ao Índice](../INDEX.md)

