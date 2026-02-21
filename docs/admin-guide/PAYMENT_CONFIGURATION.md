# 💳 Configuração de Pagamentos (MercadoPago + Stripe)

> **Última atualização:** 21/02/2026

O PDL suporta dois gateways de pagamento para depósitos na Carteira dos jogadores: **Mercado Pago** (foco no Brasil) e **Stripe** (internacional). Ambos são configurados via variáveis de ambiente e ativados no `settings.py`.

---

## 1. Configuração via Variáveis de Ambiente

Defina as chaves no arquivo `.env` do projeto:

### Mercado Pago
```env
# Mercado Pago
MP_PUBLIC_KEY=APP_USR-XXXXXX-XXXXXX-XXXXXX
MP_ACCESS_TOKEN=APP_USR-XXXXXX-XXXXXX-XXXXXX
```

### Stripe
```env
# Stripe
STRIPE_PUBLIC_KEY=pk_live_XXXXXXXXXXXXXXXX
STRIPE_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXX
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXX
```

> 🔐 **Nunca commite as chaves no repositório.** Utilize sempre `.env` fora do controle de versão.

---

## 2. Ativando os Gateways no Painel

### Verificando quais estão ativos
As integrações são ativadas automaticamente quando as variáveis de ambiente estão presentes. Para verificar:
1. Entre no painel como admin.
2. Ao criar um novo pedido, os métodos disponíveis são exibidos com base nas variáveis configuradas.

---

## 3. Fluxo de Pagamentos (MercadoPago)

### Sucesso
Webhook/Redirect: `/app/payment/mercadopago/sucesso/`

O sistema valida o pagamento e credita o saldo automaticamente.

### Erro
Redirect: `/app/payment/mercadopago/erro/`

### Pendente
Redirect: `/app/payment/mercadopago/pendente/`

### Notificações (IPN)
URL de notificação: `/app/payment/mercadopago/notificacao/`

> Configure essa URL no **Painel do Mercado Pago → Integrações → Notificações IPN**.

---

## 4. Fluxo de Pagamentos (Stripe)

### Sucesso
Redirect: `/app/payment/stripe/sucesso/`

### Erro
Redirect: `/app/payment/stripe/erro/`

### Webhook
URL: `/app/payment/stripe/webhook/`

> Configure esse endpoint no **Painel da Stripe → Developers → Webhooks**, com o evento `payment_intent.succeeded`.

---

## 5. Monitorando Pedidos

Acesse os relatórios de pedidos em:
- **Todos os pedidos:** [`/app/accountancy/orders-payments-report/`](ACCOUNTANCY_GUIDE.md)
- **Pedidos pendentes:** `/app/payment/pending/`

---

## 6. Confirmação Manual de Pagamento

Para pedidos pendentes que não foram confirmados automaticamente (ex: falha no webhook):

1. Acesse `/app/payment/pending/`.
2. Localize o pedido pelo ID ou usuário.
3. Clique em **"Confirmar Pagamento"** (`/app/payment/order/<id>/confirm/`).
4. O saldo é creditado manualmente na carteira do usuário.

---

## 7. Sistema de Bônus em Depósitos

Ao criar um pedido de pagamento, o sistema calcula automaticamente os bônus usando a lógica configurada pelo administrador.

- Para visualizar o bônus antes de confirmar: `/app/payment/calcular-bonus/` (AJAX)
- Os bônus aparecem como **Saldo Bônus** na carteira do usuário.
- Configure os percentuais de bônus no painel de configurações do servidor.

---

## Documentação Relacionada

- 💰 [Sistema de Bônus de Compras](../features/PURCHASE_BONUS_SYSTEM.md)
- 📊 [Relatório de Pedidos](ACCOUNTANCY_GUIDE.md)
- 🔑 [Variáveis de Ambiente](../installation/VARIABLES_ENVIRONMENT.md)

---

[ Voltar ao Índice](../INDEX.md)

