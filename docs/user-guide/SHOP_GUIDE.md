# 🛒 Guia da Loja

> **Última atualização:** 21/02/2026

A **Loja** do PDL permite comprar itens e pacotes de itens para o seu personagem diretamente com o saldo da sua carteira.

---

## 1. Acessando a Loja

Acesse `/app/shop/` no menu lateral. A loja exibe:
- **Itens individuais:** Itens avulsos com preço e quantidade unitária.
- **Pacotes:** Conjuntos de itens com valor total reduzido.

A listagem é paginada — 6 itens e 6 pacotes por página.

---

## 2. Adicionando ao Carrinho

### Itens Individuais
1. Clique em **"Adicionar ao Carrinho"** no item desejado.
2. Informe a **quantidade** (máximo 99 por item).
3. O item é adicionado ao seu carrinho automaticamente.

### Pacotes
1. Clique em **"Adicionar Pacote"** no pacote desejado.
2. Para adicionar mais de uma unidade, basta clicar novamente.

---

## 3. Gerenciando o Carrinho

Acesse `/app/shop/cart/` para visualizar tudo que está no seu carrinho:

| Ação | Como fazer |
|------|-----------|
| **Remover item individual** | Clique no ícone de lixeira ao lado do item |
| **Remover pacote** | Clique no ícone de lixeira ao lado do pacote |
| **Esvaziar carrinho** | Botão "Limpar Carrinho" no rodapé |

---

## 4. Usando Cupom de Desconto

Se o administrador forneceu um cupom:
1. No carrinho, localize o campo **"Código Promocional"**.
2. Informe o código e clique em **"Aplicar"**.
3. O desconto será refletido no total do carrinho.

---

## 5. Pagamento com Saldo Bônus

Se você possui **Saldo Bônus** na carteira:
1. Ative a opção **"Usar Bônus"** no carrinho.
2. O sistema usa automaticamente o bônus disponível — o restante é debitado do saldo principal.

---

## 6. Finalizando a Compra (Checkout)

1. No carrinho, selecione o **personagem que receberá os itens** no dropdown.
2. Confirme que o personagem listado é válido e pertence à sua conta.
3. Clique em **"Finalizar Compra"**.
4. O valor é debitado da carteira e os itens vão para o **inventário PDL** do personagem.

> ⚠️ O personagem deve pertencer à sua conta vinculada. Itens são entregues no inventário interno do PDL — acesse **Servidor → Inventário** para retirar os itens no jogo.

---

## 7. Histórico de Compras

Acesse `/app/shop/purchases/` para ver todas as suas compras anteriores com detalhes de:
- Data da compra
- Itens adquiridos
- Valor pago (saldo principal + bônus)
- Personagem de entrega

---

## Documentação Relacionada

- 💰 [Carteira e Pagamentos](WALLET_AND_PAYMENTS.md)
- 🎒 Inventário — para retirar seus itens no jogo

---

[ Voltar ao Índice](../INDEX.md)

