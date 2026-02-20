## Guia do Usuário – Pagamentos, Bônus e Carteira

Este guia explica como adicionar saldo, entender o bônus, acompanhar pagamentos e usar sua carteira para transferências. Tudo aqui é pensado para usuários (não precisa ser técnico).

### O que você consegue fazer
- Adicionar saldo com métodos de pagamento suportados (Mercado Pago e Stripe)
- Ver antecipadamente se sua compra tem bônus e quanto você vai receber
- Acompanhar o status do pagamento em tempo real
- Ver seu saldo normal e o saldo de bônus na carteira, com histórico
- Transferir para seus personagens do servidor (usando saldo normal ou bônus, quando habilitado)
- Transferir para outro jogador (saldo normal)

---

### 1) Como adicionar saldo
1. Acesse: `/app/payment/new/`.
2. Informe o valor que deseja comprar (em R$) e escolha o método de pagamento.
3. Veja, na própria página, as regras de bônus ativas e use o botão/calculadora para simular seu bônus.
4. Clique para continuar. Você será levado aos detalhes do pedido.
5. Na tela de detalhes do pedido: clique em “Iniciar pagamento” para abrir o checkout do provedor (Mercado Pago ou Stripe).

Após o pagamento, o sistema confirma automaticamente. Se ocorrer demora na confirmação por parte do provedor, o sistema tenta novamente e também mostra páginas de sucesso/pendente.

- Criar/visualizar pedido: `/app/payment/new/`
- Detalhes do pedido: `/app/payment/order/<pedido_id>/`
- Iniciar pagamento: `/app/payment/order/<pedido_id>/confirm/`

Sugestão: se já tiver um pedido pendente do mesmo valor e método nos últimos minutos, o sistema reaproveita automaticamente (você não cria duplicado sem querer).

---

### 2) Como ver o bônus antes de pagar
O bônus depende de faixas de valor (ex.: acima de R$ X recebe Y%). Você pode simular o bônus:

- Endpoint de simulação (a página usa isso nos bastidores): `/app/payment/calcular-bonus/` (retorna o quanto de bônus você receberá e o total creditado).

Na prática, na página de novo pedido (`/app/payment/new/`) você verá o bônus estimado ao informar o valor.

---

### 3) Acompanhar e cancelar pedidos
- Ver seus pedidos pendentes: `/app/payment/pending/`
- Ver status do pagamento (usado pela página em tempo real): `/app/payment/status-pagamento/?pagamento_id=<id>`
- Cancelar um pedido pendente: `/app/payment/cancel-order/<pedido_id>/` (apenas enquanto estiver pendente)

Em caso de sucesso no provedor, você também pode cair em páginas de retorno:
- Mercado Pago: sucesso `/app/payment/mercadopago/sucesso/`, erro `/app/payment/mercadopago/erro/`, pendente `/app/payment/mercadopago/pendente/`
- Stripe: sucesso `/app/payment/stripe/sucesso/`, erro `/app/payment/stripe/erro/`

Observação: essas páginas confirmam o crédito se, por algum motivo, o aviso automático do provedor tiver demorado.

---

### 4) Onde ver seu saldo e histórico
Acesse sua carteira:
- Dashboard da carteira: `/app/wallet/dashboard/`

O que você vê lá:
- Seu saldo normal (usado para compras e transferências comuns)
- Seu saldo de bônus (créditos extras de campanhas)
- Histórico combinado de movimentações (entradas e saídas), incluindo origem/destino e descrição

---

### 5) Transferir para o servidor (seus personagens)
Use quando quiser enviar valores da carteira para um personagem do jogo.

- Rota: `/app/wallet/transfer/server/`

Passos gerais:
1. Escolha o personagem de destino (o sistema lista seus personagens).
2. Informe o valor (limites podem existir, ex.: R$1,00 a R$1.000,00).
3. Confirme sua senha.
4. Escolha a origem do saldo:
   - Saldo normal
   - Saldo bônus (aparece e funciona somente quando essa função estiver habilitada pelo sistema)
5. Conclua a transferência e aguarde a confirmação.

Notas importantes:
- Se o personagem estiver online e o sistema exigir offline, você verá um aviso para sair do jogo.
- Quando a opção de bônus estiver habilitada, você verá no formulário a seleção “usar saldo bônus”.

---

### 6) Transferir para outro jogador
Use quando quiser enviar valores da sua carteira para outra pessoa.

- Rota: `/app/wallet/transfer/player/`

Passos gerais:
1. Informe o nome do jogador de destino (exatamente como o usuário do sistema).
2. Informe o valor (respeitando os limites informados na tela).
3. Confirme sua senha.
4. Conclua a transferência.

Notas:
- Você não pode transferir para você mesmo.
- Essa transferência utiliza o saldo normal da sua carteira.

---

### 7) Dúvidas frequentes (FAQ)
**Quando o crédito cai na carteira?**
Geralmente logo após a aprovação pelo provedor (Mercado Pago/Stripe). Em alguns casos pode haver breve atraso; as páginas de sucesso e o acompanhamento de status lidam com isso.

**Onde vejo quanto recebi de bônus?**
Na criação do pedido você já vê a previsão. Depois de pago, na carteira (`/app/wallet/dashboard/`) você vê as entradas tanto no saldo normal quanto no saldo de bônus.

**Posso usar o bônus para tudo?**
O uso do bônus é controlado pelo sistema. Atualmente, a transferência para servidor pode permitir bônus (se habilitada). Outras utilizações podem ser restritas.

**Como sei se a opção de usar bônus para servidor está ativa?**
Se estiver ativa, a tela de transferência para servidor mostrará a opção “usar saldo bônus”. Caso não veja, é porque não está disponível no momento.

**Posso cancelar um pedido?**
Sim, enquanto estiver pendente: `/app/payment/cancel-order/<pedido_id>/`.

**Meu pagamento foi aprovado no provedor, mas não caiu. E agora?**
Atualize a página de pendências/status. Se necessário, acesse a página de sucesso correspondente ao método (ela força uma verificação extra). Persistindo, aguarde alguns minutos e entre em contato com o suporte.

---

### 8) Links rápidos
- Adicionar saldo: `/app/payment/new/`
- Pedidos pendentes: `/app/payment/pending/`
- Carteira (saldos e histórico): `/app/wallet/dashboard/`
- Transferir para servidor: `/app/wallet/transfer/server/`
- Transferir para jogador: `/app/wallet/transfer/player/`

---

### 9) Boas práticas
- Revise o valor antes de iniciar o checkout.
- Guarde o comprovante de pagamento do provedor.
- Não compartilhe sua senha e sempre confirme as informações antes de transferir.


