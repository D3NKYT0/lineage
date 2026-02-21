# 🔗 PDL 1.16.0 — Era das Contas Vinculadas

> **Última atualização:** 20/02/2026

## Visão Geral
A atualização 1.16.0 é inteiramente dedicada ao ecossistema de contas vinculadas: o painel identifica automaticamente o dono mestre de cada e-mail, permite alternar a conta ativa do jogo em segundos, traz delegação guiada para contra mestres e acrescenta slots/compras para quem precisa ir além do limite padrão. Tudo abaixo está escrito para jogadores e gestores não técnicos, mas cada item aponta exatamente para o trecho do código/template em que o recurso foi implementado.

---

## 1. Quem manda no e-mail?
O conceito de **Conta Mestre** ficou mais visível. O modelo `EmailOwnership` continua garantindo que o primeiro usuário a verificar um e-mail passa a ser o administrador natural de todas as contas do Lineage 2 que usam esse endereço:

```145:154:apps/main/home/models.py
class EmailOwnership(BaseModel):
    email = models.EmailField(unique=True, verbose_name=_("E-mail"))
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='owned_emails',
                              verbose_name=_("Conta Mestre"))
```

Se precisar de um passo a passo avançado, o manual `docs/MULTI_ACCOUNT_MANAGEMENT.md` detalha modelos, fluxos e APIs que sustentam o recurso:

```1:52:docs/MULTI_ACCOUNT_MANAGEMENT.md
## Gerenciamento de múltiplas contas (Contra Mestre)
...
- **Conta ativa**: o login do jogo atualmente selecionado na sessão.
- **Contra mestre**: usuário do PDL com permissão delegada.
- **Conta mestre do e-mail**: registrada no modelo EmailOwnership.
...
1. Acesse Servidor > Conta > Gerenciar contas.
2. Use o seletor "Conta ativa" para escolher o login.
```

---

## 2. Tour pelas telas atualizadas

### `/pages/dashboard/` — Botão “?” e explicação amigável
O botão “?” no cabeçalho do painel abre um modal com tudo que você precisa saber sobre contas mestres, delegações e alertas ao trocar de e-mail. O modal e o botão ficam em `apps/main/home/templates/dashboard_custom/dashboard.html`:

```338:724:apps/main/home/templates/dashboard_custom/dashboard.html
<button ... data-bs-target="#multiAccountModal" title="{% trans 'Sobre Conta Mestre e Múltiplas Contas' %}">
  <i class="fas fa-question-circle me-1"></i>{% trans "?" %}
</button>
...
<div class="modal fade" id="multiAccountModal" ...>
  <h6 class="text-info">O que é a Conta Mestre?</h6>
  <ul>
    <li>Quando você verifica seu e-mail ...</li>
    <li>A Conta Mestre pode delegar acesso...</li>
  </ul>
  <a href="{% url 'server:manage_lineage_accounts' %}" class="btn">Gerenciar Contas</a>
</div>
```

Resumo para o jogador:
- O painel explica, no próprio dashboard, como funciona a hierarquia das contas.
- Um atalho direto leva para `/app/server/account/manage/` para quem quer agir imediatamente.

### `/app/profile/` — Alertas claros sobre vínculo
O perfil ganhou alertas visuais que deixam explícito se a sua conta está vinculada à mestre de outro usuário ou se foi desvinculada recentemente:

```888:945:apps/main/home/templates/pages/profile.html
{% if not account_is_linked and original_email_master_owner %}
  <div class="alert alert-info">Esta conta foi desvinculada do sistema...</div>
{% endif %}
{% if account_is_linked and not is_email_master_owner and email_master_owner %}
  <div class="alert alert-warning">
    Conta associada à Conta Mestre {{ email_master_owner.username }}
  </div>
{% endif %}
```

Também há um lembrete fixo sobre como o e-mail define quem manda nas contas vinculadas, reforçando boas práticas antes de editar informações sensíveis.

### `/app/profile/edit/` — Mensagens educativas antes de salvar
Na edição do perfil, o aviso amarelo deixa claro o que acontece ao trocar o e-mail: você pode perder o status de mestre ou passar a responder a outro dono. O alerta fica logo abaixo do campo de e-mail para ninguém salvar “sem querer”:

```395:418:apps/main/home/templates/pages/edit_profile.html
<div class="alert alert-warning">
  Atenção: Alteração de E-mail
  <li>Se você alterar para um e-mail que já possui uma conta mestre...</li>
  <li>Após alterar o e-mail, você precisará verificá-lo novamente.</li>
</div>
```

### `/app/server/account/dashboard/` — Central da conta ativa
O dashboard da conta Lineage agora mostra:
- Qual login está ativo (com badge + botão “Alterar conta”).
- Aviso caso a conta atual esteja subordinada a outro mestre.
- Atalhos para alterar senha do jogo, comprar slots e criar novas contas vinculadas.

```492:700:apps/lineage/server/templates/l2_accounts/dashboard.html
<span class="badge ...">{% trans "Conta ativa" %}: {{ active_account_login }}</span>
<a href="{% url 'server:manage_lineage_accounts' %}" class="change-account-btn">Alterar conta</a>
...
<a href="{% url 'server:purchase_link_slot' %}" class="service-btn service-btn-slots">Comprar Slots</a>
{% if is_email_master_owner %}
  <a href="{% url 'server:create_master_account' %}" class="service-btn service-btn-create">
    Criar Nova Conta Vinculada
  </a>
{% endif %}
```

### `/app/server/account/manage/` — Trocar conta ativa e delegar
Esta tela virou o “QG” das contas:
- Seleciona a conta ativa (sem sair da página).
- Mostra alertas diferentes para mestres, subordinados ou contas desvinculadas.
- Permite adicionar/remover contra mestres e listar delegações recebidas.
- Exibe as contas “auto vinculadas” com opção de desvincular com confirmação extra se ela estiver ativa.

```150:405:apps/lineage/server/templates/l2_accounts/manage_accounts.html
<select name="account_login">... {{ account.login }} — {{ account.role_label }}</select>
...
{% if account_is_linked and is_email_master_owner %}
  <form action="{% url 'server:add_contra_mestre' %}">
    <select name="account_login">...</select>
  </form>
{% endif %}
...
{% for linked_account in linked_accounts_info %}
  <form method="post" action="{% url 'server:unlink_lineage_account' %}">
    <input type="hidden" name="account_login" value="{{ linked_account.account_login }}">
    <button class="btn btn-sm btn-danger">Desvincular</button>
  </form>
{% endfor %}
```

### `/app/server/account/purchase-slot/` — Comprar slots extras
Para quem precisa vincular mais de três contas, a nova página mostra quantos slots existem, quantos estão em uso, saldo da carteira e histórico de compras:

```432:538:apps/lineage/server/templates/l2_accounts/purchase_link_slot.html
<div class="stat-value-gamer text-primary">{{ total_slots }}</div>
...
<label for="quantity">Quantidade de Slots</label>
<option value="5">5 slots - R$ {{ prices.5 }}</option>
...
{% for purchase in purchase_history %}
  <span class="history-title">Compra de {{ purchase.slots_purchased }} slot(s)</span>
{% endfor %}
```

### `/app/server/account/create-master-account/` — Criar nova conta direto da mestre
Quem já é mestre e tem slots sobrando consegue criar outra conta PDL + L2 de uma vez só, usando o mesmo e-mail. O formulário coleta usuário e senhas separadas (uma para o portal, outra para o jogo) com validações em tempo real:

```187:529:apps/lineage/server/templates/l2_accounts/create_master_account.html
<div class="slots-info-value available">{{ available_slots }}</div>
<input name="username" pattern="[a-zA-Z0-9]+" maxlength="16">
...
<input type="password" id="password_pdl" minlength="12">
<input type="password" id="password_l2" minlength="6" pattern="[A-Za-z0-9]+">
<script>
  function validatePasswordFormatPDL(password) { ... }
  function validatePasswordFormatL2(password) { ... }
</script>
```

---

## 3. O que muda na prática
- **Trocar de conta**: Agora é só abrir “Gerenciar contas” e escolher o login; o painel inteiro passa a agir com aquele personagem.
- **Delegar com segurança**: Quem é mestre vê exatamente quais contas podem ser compartilhadas e remove acessos com um clique.
- **Escalar com slots**: Chegou no limite grátis? Compre slots, acompanhe o histórico e crie novas contas vinculadas direto do painel.
- **Alertas contextuais**: Em todas as telas (dashboard, perfil, edição e servidor) o usuário sempre sabe se está como mestre, subordinado ou desvinculado.

Resultado: menos suporte manual, menos confusão sobre quem controla cada login e um fluxo completo de autogestão para servidores com equipes grandes.

---

## Como experimentar
1. Entre no painel e clique no “?” do dashboard para entender o conceito.
2. Edite seu perfil em `/app/profile/edit/` e veja os avisos antes de trocar o e-mail.
3. Vá até `Servidor > Conta > Gerenciar` para trocar a conta ativa e delegar acessos.
4. Se precisar de mais contas, compre slots e crie novas contas vinculadas na própria UI.

Bem-vindo à versão 1.16.0 — onde o PDL cuida das suas contas múltiplas de ponta a ponta! 🎯

