## Gerenciamento de múltiplas contas (Contra Mestre)

Este recurso permite que um usuário delegue diferentes contas do Lineage 2 para outros membros da equipe (contra mestres) dentro do painel PDL, mantendo auditoria e troca rápida entre contas.

### Conceitos

- **Conta ativa**: o login do jogo atualmente selecionado na sessão. Todos os módulos sensíveis (inventário, carteira, shop, serviços e marketplace) utilizam este login para consultar personagens e executar operações no banco do jogo.
- **Contra mestre**: usuário do PDL com permissão delegada para operar uma conta que não é a sua principal. Cada delegação é registrada em `ManagedLineageAccount`.
- **Proprietário**: usuário cujo UUID está vinculado diretamente ao login do jogo (`linked_uuid`). Somente o proprietário pode criar ou remover delegações.
- **Conta mestre do e-mail (Email Master)**: quando mais de uma conta do PDL compartilha o mesmo e-mail, a primeira que confirmar o endereço se torna automaticamente a "conta mestre" desse e-mail. Isso é registrado no modelo `EmailOwnership`. A conta mestre pode gerenciar todas as contas do Lineage 2 que possuem aquele e-mail.
- **Vinculação automática**: quando você salva seu perfil (independente de ter alterado o e-mail ou não), o sistema verifica se o seu e-mail já possui uma conta mestre. Se sim, a sua conta do Lineage 2 (username) é automaticamente vinculada ao UUID da conta mestre no banco do jogo. **Importante**: apenas a conta que está sendo editada é vinculada, outras contas com o mesmo e-mail não são afetadas.

### Vinculação de Contas do Lineage 2

#### Vinculação Automática ao Salvar Perfil

Quando você salva seu perfil (em `/app/profile/edit/`), o sistema verifica automaticamente:

1. **Se o seu e-mail possui uma conta mestre**: O sistema verifica se existe um `EmailOwnership` para o seu e-mail.
2. **Se sim, vincula apenas a sua conta**: Apenas a conta do Lineage 2 correspondente ao seu username é vinculada ao UUID da conta mestre.
3. **Outras contas não são afetadas**: Se existem outras contas do Lineage 2 com o mesmo e-mail, elas **não** são vinculadas automaticamente nesta operação.

**Exemplo:**
- `admin` é a conta mestre do e-mail `exemplo@email.com`
- `denkyto` e `denky` também têm esse e-mail no banco do Lineage 2
- Você edita o perfil de `denkyto` e salva
- **Resultado**: Apenas `denkyto` é vinculado ao `admin`. `denky` permanece como estava.

#### Vinculação Manual

Para vincular uma conta do Lineage 2 manualmente:

1. Acesse `Servidor > Conta > Vincular conta` (`/app/server/account/link-lineage-account/`).
2. Informe a senha da conta do Lineage 2.
3. (Opcional) Solicite um código de verificação por e-mail para maior segurança.
4. A conta será vinculada ao seu UUID no banco do Lineage 2.

**Importante**: A vinculação manual vincula apenas a conta correspondente ao seu username. Outras contas não são afetadas.

### Fluxo de Gerenciamento

1. Acesse `Servidor > Conta > Gerenciar contas` (`/app/server/account/manage/`).
2. Use o seletor "Conta ativa" para escolher qual login deseja operar. O badge da conta ativa também aparece no dashboard da conta.
3. Para adicionar um contra mestre, informe:
   - Login do jogo (precisa estar vinculado ao seu usuário).
   - Username do usuário do PDL que atuará como contra mestre.
   - Observações (opcional) com as orientações desejadas.
4. Cada contra mestre pode receber acesso a múltiplas contas. O painel lista:
   - Contas que você delegou (com ação de remover acesso).
   - Contas delegadas para você (incluindo quem concedeu o acesso).
   - Contas vinculadas automaticamente (via `linked_uuid` ou e-mail).

### Comportamento de Vinculação

#### Quando o e-mail é alterado

Se você alterar o e-mail no perfil e o novo e-mail já possui uma conta mestre:
- A sua conta do Lineage 2 (username) é vinculada ao UUID da conta mestre.
- O campo `email` no banco do Lineage 2 é atualizado para o novo e-mail.
- O campo `linked_uuid` é atualizado para o UUID da conta mestre.

#### Quando o e-mail não é alterado

Se você salvar o perfil sem alterar o e-mail:
- O sistema verifica se o e-mail atual possui uma conta mestre.
- Se sim, vincula apenas a sua conta do Lineage 2 ao UUID da conta mestre.
- Outras contas com o mesmo e-mail **não** são vinculadas automaticamente.

#### Desvincular uma conta

Para desvincular uma conta do Lineage 2:
1. Acesse `Servidor > Conta > Gerenciar contas`.
2. Na seção "Contas delegadas para você", clique em "Desvincular" na conta desejada.
3. A conta terá seu `linked_uuid` definido como `NULL` no banco do Lineage 2.
4. O campo `email` **não** é alterado (permanece como estava).

### Segurança

- Toda troca de contexto valida se o usuário possui permissão ativa na conta selecionada.
- Operações críticas (transferências, shop, serviços) continuam exigindo autenticação local (senha do PDL) e respeitam as mesmas verificações de PIN/2FA já existentes.
- Delegações podem ser revogadas a qualquer momento pelo proprietário ou por um superusuário.
- A vinculação automática ocorre apenas para a conta específica que está sendo editada, garantindo que outras contas não sejam afetadas inadvertidamente.

### APIs

- Endpoints do dashboard podem receber o parâmetro `account_login` (query string ou corpo) para definir explicitamente a conta alvo. Sem esse parâmetro, a API usa o mesmo contexto registrado na sessão web.

