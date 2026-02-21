# 💰 Carteira e Pagamentos

> **Última atualização:** 21/02/2026

A **Carteira** é o centro financeiro do painel PDL. Aqui você gerencia dois tipos de saldo: o **Saldo Principal** (obtido via depósitos reais) e o **Saldo Bônus** (créditos promocionais).

---

## 1. Acessando sua Carteira

Acesse `/app/wallet/dashboard/` ou clique em **"Carteira"** no menu lateral.

Você verá:
- **Saldo Principal (R$):** Valor disponível para compras na loja, leilões e marketplace.
- **Saldo Bônus (R$):** Créditos extras concedidos por promoções — usados conforme as regras do servidor.
- **Extrato:** Histórico paginado de todas as transações (entradas, saídas e bônus).

---

## 2. Como Fazer um Depósito

Para adicionar crédito à sua carteira:

1. Acesse **Pagamentos → Novo Pedido** (`/app/payment/new/`).
2. Informe o **valor desejado** — o sistema calcula automaticamente os bônus, se houver promoção ativa.
3. Escolha o **método de pagamento**:

| Gateway | Como pagar |
|---------|-----------|
| **Mercado Pago** | Pix, cartão de crédito/débito, boleto |
| **Stripe** | Cartão de crédito internacional |

4. Siga o fluxo de pagamento do gateway escolhido.
5. Após a confirmação do pagamento, o saldo é **creditado automaticamente** na sua carteira.

> **Pagamentos pendentes:** Acesse `/app/payment/pending/` para verificar pedidos em processamento.

---

## 3. Transferências Jogo ↔ Carteira

### 3.1 Enviar Saldo para o Servidor (Carteira → Jogo)

Converta seu saldo da carteira em moedas do jogo no seu personagem:

1. Acesse **Carteira → Enviar para Servidor** (`/app/wallet/transfer/server/`).
2. Escolha o personagem de destino (deve estar **offline**).
3. Informe o valor em R$ a transferir.
4. Confirme. As moedas aparecerão no inventário do personagem.

> O administrador define qual item/moeda é creditado e a taxa de conversão.

### 3.2 Retirar do Servidor para a Carteira (Jogo → Carteira)

Converta moedas do personagem de volta para saldo na carteira:

1. Acesse **Carteira → Retirar do Servidor** (`/app/wallet/transfer/from-server/`).
2. Selecione o personagem com moedas disponíveis.
3. Informe a quantidade de moedas.
4. Insira sua senha PDL para confirmar.
5. O saldo é creditado na carteira após desconto da **taxa de retirada** (se configurada).

> ⚠️ O personagem deve estar **offline** para a retirada funcionar.

### 3.3 Transferir para Outro Jogador

Envie saldo da sua carteira para outro usuário do PDL:

1. Acesse **Carteira → Transferir para Jogador** (`/app/wallet/transfer/player/`).
2. Informe o usuário destinatário e o valor.
3. Confirme a operação.

---

## 4. Fichas (Tokens para Minigames)

Você pode comprar **fichas** para usar nos minigames do painel:

1. Na carteira, clique em **"Comprar Fichas"**.
2. Informe a quantidade desejada (máximo 10.000 por transação).
3. Escolha entre usar o **Saldo Principal** ou o **Saldo Bônus**.
4. As fichas são creditadas imediatamente no seu perfil.

> Cada ficha custa R$0,10.

---

## 5. Histórico de Transações

O extrato exibe todas as movimentações em ordem cronológica, incluindo:
- **Tipo:** Entrada ou Saída
- **Valor:** Em R$
- **Descrição:** Motivo da transação
- **Data e Hora**

> Transações normais e de bônus são exibidas em conjunto, com marcação visual diferenciando o tipo.

---

## Documentação Relacionada

- 🛒 [Guia da Loja](SHOP_GUIDE.md)
- 🏷️ [Guia do Leilão](AUCTION_GUIDE.md)
- 💳 [Configuração de Pagamentos](../admin-guide/PAYMENT_CONFIGURATION.md) *(para administradores)*

---

[ Voltar ao Índice](../INDEX.md)

