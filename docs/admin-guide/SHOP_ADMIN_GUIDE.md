# 🛒 Gerenciando a Loja — Guia do Administrador

> **Última atualização:** 21/02/2026

O administrador da loja pode cadastrar itens, criar pacotes, gerenciar promoções e cupons de desconto diretamente pelo painel de gerenciamento.

> Acesso restrito a usuários com permissão de **Staff**.

---

## 1. Acessando o Painel da Loja

Navegue para `/app/shop/manager/dashboard/` para ver o resumo geral da loja.

---

## 2. Gerenciando Itens

**URL:** `/app/shop/manager/items/`

### Cadastrando um Item
1. Clique em **"Adicionar Item"**.
2. Preencha:
   - **Nome:** Nome exibido na loja (ex: "Sword of Despair")
   - **Item ID:** ID numérico do item no banco do Lineage 2
   - **Preço (R$):** Valor em reais
   - **Quantidade:** Quantidade entregue por compra (ex: 5 = o jogador recebe 5 unidades)
   - **Ativo:** Marque para exibir na loja
3. Salve.

### Editando ou Desativando
- Acesse o item na listagem e altere os campos desejados.
- Desmarque **"Ativo"** para ocultar o item da loja sem excluí-lo.

---

## 3. Gerenciando Pacotes

**URL:** `/app/shop/manager/packages/`

Pacotes são conjuntos de itens vendidos por um preço único (geralmente com desconto em relação à soma individual).

### Criando um Pacote
1. Clique em **"Adicionar Pacote"**.
2. Defina o nome, preço total e status (ativo/inativo).
3. Salve o pacote.

### Adicionando Itens ao Pacote
1. Acesse a edição do pacote: `/app/shop/manager/package/edit/<id>/`.
2. Clique em **"Adicionar Item ao Pacote"** (`/app/shop/manager/package/<id>/add_item/`).
3. Selecione um item do catálogo e defina a quantidade inclusa.

### Removendo Itens do Pacote
- Na edição do pacote, clique no ícone de remover ao lado do item: `/app/shop/manager/package/remove_item/<item_id>/`.

---

## 4. Gerenciando Promoções e Cupons

**URL:** `/app/shop/manager/promotions/`

### Criando um Cupom de Desconto
1. Acesse a lista de promoções.
2. Clique em **"Adicionar Promoção"**.
3. Preencha:
   - **Código:** O código que o usuário digitará (ex: `PROMO10`)
   - **Tipo:** Percentual ou valor fixo
   - **Valor do Desconto**
   - **Data de Expiração**
   - **Ativo:** Marque para ativar o cupom

### Boas Práticas
- Defina sempre uma **data de expiração** para cupons promocionais.
- Desative cupons manualmente se quiser encerrá-los antes do prazo.
- Monitore o uso dos cupons via [Relatório de Pedidos](ACCOUNTANCY_GUIDE.md).

---

## 5. Saldo Bônus na Compra

O sistema suporta uso misto de **saldo principal** e **saldo bônus** no checkout:
- O jogador pode ativar a opção de usar bônus no carrinho.
- O sistema desconta primeiro o bônus disponível e o restante do saldo principal.
- O relatório de compras discrimina exatamente quanto foi pago em cada tipo.

---

## Documentação Relacionada

- 🛒 [Guia da Loja — Usuário](../user-guide/SHOP_GUIDE.md)
- 📊 [Relatório Financeiro](ACCOUNTANCY_GUIDE.md)
- 💳 [Configurar Pagamentos](PAYMENT_CONFIGURATION.md)

---

[ Voltar ao Índice](../INDEX.md)

