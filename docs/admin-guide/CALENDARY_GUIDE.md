# 📅 Calendário de Eventos — Guia do Administrador

> **Última atualização:** 21/02/2026

O **Calendário do PDL** exibe os eventos do servidor para os jogadores, como raids, eventos especiais, manutenções e promoções. O administrador controla quais eventos são exibidos e quando.

---

## 1. Acessando o Painel do Calendário

Acesse `/app/calendary/manager/` para o painel de gerenciamento de eventos.

> Restrito a usuários com permissão de **Staff**.

---

## 2. Listando Eventos

**URL:** `/app/calendary/manager/events/`

Exibe todos os eventos cadastrados com título, data, status e opções de edição/exclusão.

---

## 3. Criando um Evento

**URL:** `/app/calendary/manager/event/create/`

Preencha os campos:

| Campo | Descrição |
|-------|-----------|
| **Título** | Nome do evento exibido no calendário |
| **Descrição** | Detalhes do evento (texto livre) |
| **Data e Hora de Início** | Quando o evento começa |
| **Data e Hora de Fim** | Quando o evento termina (para eventos contínuos) |
| **Cor** | Cor do bloco no calendário (hex, ex: `#e74c3c`) |
| **Ativo** | Marque para exibir publicamente |

---

## 4. Editando um Evento

**URL:** `/app/calendary/manager/event/<id>/edit/`

Altere qualquer campo do evento. A atualização é imediata no calendário público.

---

## 5. Excluindo um Evento

**URL:** `/app/calendary/manager/event/<id>/delete/`

Remove o evento permanentemente do calendário. Esta ação não pode ser desfeita.

---

## 6. Visualização pelos Jogadores

Os jogadores veem o calendário em `/app/calendary/dashboard/`, com todos os eventos ativos exibidos em formato de calendário interativo.

Os eventos são carregados via API AJAX (`/app/calendary/api/events/`) para uma experiência fluida e responsiva.

---

## Documentação Relacionada

- 🗺️ [Roadmap do Servidor](ROADMAP_ADMIN_GUIDE.md)
- 📰 [Gerenciar Notícias](NEWS_ADMIN_GUIDE.md)

---

[ Voltar ao Índice](../INDEX.md)

