# 🏷️ Guia do Leilão

> **Última atualização:** 21/02/2026

O sistema de **Leilão** permite que jogadores coloquem itens à venda e que outros jogadores deem lances para arrematá-los, tudo usando o saldo da Carteira PDL.

---

## 1. Acessando o Leilão

Navegue até `/app/auction/` ou clique em **"Leilão"** no menu lateral.

A lista exibe todos os leilões ativos com:
- Nome e encantamento do item
- Vendedor
- Lance atual
- Prazo de encerramento
- Status (Ativo / Encerrado / Cancelado)

---

## 2. Dando um Lance

1. Clique no leilão desejado para ver os detalhes.
2. Clique em **"Dar Lance"** (`/app/auction/bid/<id>/`).
3. Informe o valor do lance (deve ser maior que o lance atual).
4. Confirme.

> O valor do lance é **reservado** na sua carteira. Se outro jogador der um lance maior, o valor é devolvido automaticamente e você é notificado.

---

## 3. Criando um Leilão (Vendendo um Item)

Para colocar um item à leilão:

1. Acesse `/app/auction/create/`.
2. Preencha os dados:
   - **ID do Item** no jogo
   - **Nome do Item**
   - **Encantamento** (enchant level)
   - **Quantidade**
   - **Nome do personagem vendedor**
   - **Lance mínimo (R$)**
   - **Prazo de encerramento** (data e hora)
3. Confirme para publicar o leilão.

> ⚠️ Certifique-se que o item informado está em posse do seu personagem no jogo.

---

## 4. Acompanhando Seus Leilões

- **Leilões criados por você:** Verifique o status diretamente na listagem geral filtrando pelo seu usuário.
- **Lances dados:** Os lances ativos ficam vinculados ao seu saldo da carteira como reserva.

---

## 5. Cancelando um Leilão

Se você é o vendedor e o leilão não teve lances, pode cancelá-lo:

1. Localize seu leilão na listagem.
2. Clique em **"Cancelar Leilão"** (`/app/auction/cancel/<id>/`).

> Leilões com lances ativos **não podem ser cancelados** diretamente. Entre em contato com o administrador se necessário.

---

## 6. Encerramento Automático

Leilões são encerrados automaticamente a cada **1 minuto** por uma tarefa agendada (Celery Beat):
- O vencedor é o usuário com o **maior lance** no momento do encerramento.
- O valor é debitado da carteira do vencedor e transferido para o vendedor.
- Uma **notificação** é enviada para ambos.

---

## Documentação Relacionada

- 💰 [Carteira e Pagamentos](WALLET_AND_PAYMENTS.md)
- 🛍️ [Marketplace de Personagens](../features/MARKETPLACE.md)

---

[ Voltar ao Índice](../INDEX.md)

