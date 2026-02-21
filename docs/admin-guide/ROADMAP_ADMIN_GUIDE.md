# 🗺️ Roadmap do Servidor — Guia do Administrador

> **Última atualização:** 21/02/2026

O **Roadmap** do PDL permite ao administrador publicar os planos futuros e o status de desenvolvimento do servidor para que os jogadores acompanhem o progresso.

---

## 1. Acessando o Painel do Roadmap

Navegue para `/app/roadmap/manager/` para o painel de gerenciamento.

> Restrito a usuários com permissão de **Staff**.

---

## 2. Listando Roadmaps

**URL:** `/app/roadmap/manager/roadmaps/`

Lista todos os roadmaps criados com título, status e data.

---

## 3. Criando um Roadmap

**URL:** `/app/roadmap/manager/roadmap/create/`

Preencha os campos:

| Campo | Descrição |
|-------|-----------|
| **Título** | Nome do roadmap (ex: "Atualização de Agosto 2026") |
| **Slug** | URL amigável (ex: `atualizacao-agosto-2026`) |
| **Descrição** | Texto explicativo sobre os objetivos |
| **Status** | Planejado, Em Andamento, Concluído, Cancelado |
| **Data Prevista** | Previsão de entrega |

---

## 4. Editando e Excluindo

| URL | Ação |
|-----|------|
| `/app/roadmap/manager/roadmap/<id>/` | Visualizar detalhes |
| `/app/roadmap/manager/roadmap/<id>/edit/` | Editar |
| `/app/roadmap/manager/roadmap/<id>/delete/` | Excluir |

---

## 5. Visualização pelos Jogadores

Jogadores acessam o roadmap em `/app/roadmap/` (lista de roadmaps) e `/app/roadmap/<slug>/` (detalhes de um roadmap específico).

---

## Documentação Relacionada

- 📅 [Calendário de Eventos](CALENDARY_GUIDE.md)
- 📚 [Wiki do Servidor](WIKI_ADMIN_GUIDE.md)

---

[ Voltar ao Índice](../INDEX.md)

