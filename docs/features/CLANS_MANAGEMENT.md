# Gerenciamento de Clãs — Documentação Técnica

> **Última atualização:** 22/02/2026

Sistema de recrutamento web integrado ao banco de dados do Lineage 2 (L2), permitindo que líderes de clã configurem perfis públicos e recebam inscrições de jogadores, que por sua vez podem candidatar-se a clãs recrutando usando personagens vinculados às suas contas.

---

## Visão Geral

O módulo de clãs (`apps.lineage.clans`) oferece:

1. **Listagem pública** — Clãs que estão recrutando aparecem numa página acessível a todos
2. **Perfil de clã** — MOTD, requisitos (nível, classes, foco), imagens personalizadas
3. **Dashboard do líder** — Área restrita para líderes gerenciarem inscrições e configurações
4. **Inscrições** — Jogadores se candidatam com personagem vinculado e carta de apresentação
5. **Aprovação/Rejeição** — Líderes processam inscrições pendentes no dashboard

O vínculo com o jogo é feito exclusivamente via `clan_id`: os dados de líder, membros, reputação e nível vêm do banco L2 através da classe `LineageClans` (query module).

---

## Arquitetura

### Estrutura do app

```
apps/lineage/clans/
├── models.py          # ClanProfile, RecruitmentApplication (Django ORM)
├── views.py           # ClanListView, ClanDetailView, ClanDashboardView, etc.
├── forms.py           # ClanProfileForm, RecruitmentApplicationForm
├── services.py        # Wrapper que delega para LineageClans
├── urls.py
├── admin.py
└── templates/clans/
    ├── list.html      # Lista de clãs recrutando
    ├── detail.html    # Perfil público do clã
    ├── apply.html     # Formulário de inscrição
    ├── dashboard.html # Painel do líder
    └── test_claim.html# Ferramenta de teste (dev)
```

### Modelos (Django ORM)

| Modelo | Descrição |
|--------|-----------|
| **ClanProfile** | Perfil web do clã. Campos: `clan_id`, `recruiting`, `motd`, `min_level`, `required_classes`, `focus`, `crest_image`, `banner_image`, etc. |
| **RecruitmentApplication** | Inscrição de jogador. Campos: `clan_profile`, `user`, `char_id`, `char_name`, `message`, `status` (PENDING, APPROVED, REJECTED, etc.) |

A associação com o jogo é sempre pelo `clan_id` (inteiro); não há FK para tabelas L2.

### Serviços e integração com L2

O arquivo `services.py` é um wrapper que delega para a classe `LineageClans` carregada dinamicamente:

```python
from utils.dynamic_import import get_query_class

LineageClans = get_query_class("LineageClans")
LineageClans.get_user_lead_clans(account_logins)   # Clãs onde o usuário é líder
LineageClans.get_user_characters(account_logins)   # Personagens das contas vinculadas
LineageClans.get_clan_basic_info(clan_id)          # clan_id, clan_name, clan_level
LineageClans.get_clan_full_details(clan_id)        # + leader_name, member_count, reputation
```

`LineageClans` é definida em cada módulo query (`query_default`, `query_ruacis`, `query_mobius`, etc.) e usa o schema do banco L2 correspondente. Isso garante compatibilidade com diferentes versões (Dream, ACIS, RuACIS, Mobius, etc.).

---

## Fluxo de Funcionamento

### 1. Jogador visualiza clãs recrutando

- URL: `/app/clans/` (`clans:list`)
- View: `ClanListView`
- Lista todos os `ClanProfile` com `recruiting=True`
- Template: `list.html`

### 2. Jogador acessa o perfil do clã

- URL: `/app/clans/<clan_id>/` (`clans:detail`)
- View: `ClanDetailView`
- Mostra `ClanProfile` + dados do jogo (`get_clan_full_details`) — MOTD, requisitos, estatísticas, botão de inscrição
- Template: `detail.html`

### 3. Jogador se inscreve

- URL: `/app/clans/<clan_id>/apply/` (`clans:apply`)
- View: `ApplyToClanView` (requer login)
- Formulário: escolha de personagem (dropdown de chars vinculados) + carta de apresentação
- O personagem precisa pertencer às contas vinculadas ao usuário (validação em `post`)
- Cria `RecruitmentApplication` com `status='PENDING'`
- Template: `apply.html`

### 4. Líder acessa o dashboard

- URL: `/app/clans/dashboard/` (`clans:dashboard`)
- View: `ClanDashboardView` (requer login)
- Obtém clãs em que o usuário é líder via `get_user_lead_clans(logins)` — contas vinculadas via `get_available_accounts`
- Permite trocar de clã via `?clan_id=…`
- Abas: Inscrições, Membros (em desenvolvimento), Configurações
- Template: `dashboard.html`

### 5. Líder processa inscrições

- Aprovar/Rejeitar via POST para `clans:process_application`
- URL: `/app/clans/application/<pk>/<action>/` (`approve` ou `reject`)
- View: `ProcessApplicationView` — valida que o usuário é líder do clã (via `leader_char_id` e `clan_id`) e atualiza o status
- Segurança: só processa se o personagem líder pertence às contas do usuário

### 6. Test Claim (desenvolvimento)

- URL: `/app/clans/test-claim/` (`clans:test_claim`)
- Permite simular liderança de um clã para testes locais
- Armazena clãs “mock” em `request.session['mock_lead_clans']`
- Útil quando não há dados reais de líder no banco L2

---

## Integração com o banco L2

### Classe LineageClans

A classe `LineageClans` fica em cada arquivo `query_*.py` (ex.: `query_default`, `query_ruacis`, `query_mobius`) e é carregada via `get_query_class("LineageClans")`, que usa `LINEAGE_QUERY_MODULE` para escolher o módulo.

**Métodos:**

| Método | Retorno | Uso |
|--------|---------|-----|
| `get_user_lead_clans(account_logins)` | `[{clan_id, clan_name, clan_level, leader_name, leader_id}, ...]` | Clãs em que algum personagem das contas é líder |
| `get_user_characters(account_logins)` | `[{char_id, char_name, level, clan_id}, ...]` | Personagens das contas (usa `LineageServices.find_chars`) |
| `get_clan_basic_info(clan_id)` | `{clan_id, clan_name, clan_level}` | Dados básicos do clã |
| `get_clan_full_details(clan_id)` | `{clan_id, clan_name, level, leader_name, member_count, reputation, ...}` | Dados completos (delega para `LineageStats.get_clan_details` quando existir) |
| `get_clan_members(clan_id)` | `[{char_name, online, pvpkills, pkkills, level, base...}, ...]` | Retorna os membros de um clã (respeitando acessos e estrutura de colunas) |

O SQL é adaptado ao schema: `CLAN_NAME_SOURCE` (clan_data vs clan_subpledges) e `SUBPLEDGE_FILTER` (sub_pledge_id vs type) vêm das constantes do módulo query.

### Generate Query

A classe `LineageClans` é gerada automaticamente pelo script `gerar_query.py`:

- Template: `apps/lineage/server/generate_query/classes/lineage_clans.py`
- Gera código com SQL específico para o schema detectado
- É incluída em todos os módulos query suportados (default, classic, dreamv2, dreamv3, lucerav2, l2jpremium, mobius, acis_v1, acis_v2, ruacis)

---

## URLs e Rotas

| Rota | Nome | View | Acesso |
|------|------|------|--------|
| `/app/clans/` | `clans:list` | ClanListView | Público |
| `/app/clans/<clan_id>/` | `clans:detail` | ClanDetailView | Público |
| `/app/clans/<clan_id>/apply/` | `clans:apply` | ApplyToClanView | Login |
| `/app/clans/dashboard/` | `clans:dashboard` | ClanDashboardView | Login (líder) |
| `/app/clans/test-claim/` | `clans:test_claim` | TestClaimClanView | Login |
| `/app/clans/application/<pk>/<action>/` | `clans:process_application` | ProcessApplicationView | Login (líder, POST) |

---

## Segurança e Validações

1. **Liderança** — O dashboard e o processamento de inscrições só funcionam para personagens líderes, identificados via `get_user_lead_clans` (ou mock em sessão no modo teste).
2. **Personagem na inscrição** — Quando há personagens vinculados, o formulário usa dropdown e a view confirma que `char_id` pertence às contas do usuário.
3. **Spam** — `RecruitmentApplication` tem `unique_together = ('clan_profile', 'char_id')`, evitando múltiplas inscrições do mesmo personagem no mesmo clã.
4. **CSRF** — Todos os forms POST usam `{% csrf_token %}`.

---

## Contas Vinculadas

O sistema usa `get_available_accounts(request.user)` do app `account_context` para obter os logins L2 vinculados ao usuário. Com isso:

- `get_user_lead_clans(logins)` retorna os clãs em que o usuário é líder
- `get_user_characters(logins)` retorna os personagens disponíveis para inscrição

Usuários sem contas vinculadas podem ter acesso limitado (ex.: entrada manual de char no modo fallback).

---

## Temas e Renderização

As views usam `render_theme_page(request, 'clans', 'template.html', context)` para respeitar o sistema de temas do PDL. Os templates ficam em `templates/clans/` e herdam do layout base do tema.

---

## Próximos Passos (roadmap)

- **Membros** — Aba “Membros” no dashboard com lista de membros vindos do L2
- **Convite híbrido** — Ao aprovar, opção de atualizar `char.clanid` no banco L2 quando o personagem estiver offline
- **Notificações** — Avisar jogador quando a inscrição for aprovada ou rejeitada

---

[ Voltar ao Índice de Funcionalidades](FEATURES_INDEX.md) | [ Voltar ao Índice Geral](../INDEX.md)
