# 👥 Guia de Notificações e Mensagens

> **Última atualização:** 21/02/2026

O PDL possui um sistema integrado de **notificações em tempo real** e um gerenciador completo de **amizades e chat**.

---

## 1. Notificações

### Onde Ver
O ícone de notificações no cabeçalho do painel exibe alertas em tempo real sobre:
- Leilões ganhos ou superados por outro lance
- Compras aprovadas na loja
- Transferências recebidas na carteira
- Novas solicitações de amizade
- Moderação de conteúdo (posts reprovados)
- Eventos e novidades do servidor

### Como Funciona
- Notificações são exibidas no badge do cabeçalho com contagem de não lidas.
- Ao clicar, você é direcionado à central de notificações.
- Notificações podem ser marcadas como lidas individualmente ou em bloco.

---

## 2. Sistema de Amizades

Acesse `/app/message/friends-list/` para gerenciar seus amigos no PDL.

### Adicionando um Amigo

1. Encontre o perfil do jogador (feed social ou busca).
2. Clique em **"Adicionar Amigo"**.
3. Uma solicitação de amizade é enviada para o usuário.

### Gerenciando Solicitações

| Ação | URL |
|------|-----|
| Enviar solicitação | `/app/message/send-friend-request/<user_id>/` |
| Aceitar solicitação | `/app/message/accept-friend-request/<friendship_id>/` |
| Recusar solicitação | `/app/message/reject-friend-request/<friendship_id>/` |
| Cancelar solicitação enviada | `/app/message/cancel-friend-request/<friendship_id>/` |
| Remover amizade | `/app/message/remove-friend/<friendship_id>/` |

### Lista de Amigos

Em `/app/message/friends-list/` você vê:
- Todos os seus amigos confirmados.
- Solicitações pendentes (recebidas e enviadas).
- Opção de buscar usuários por nome.

---

## 3. Chat

O chat é integrado com WebSockets (Django Channels) para comunicação em **tempo real** com seus amigos.

### Como Acessar
1. Acesse a lista de amigos em `/app/message/index/`.
2. Selecione um amigo para abrir a conversa.
3. Digite sua mensagem e envie.

### Funcionalidades
- Mensagens em tempo real sem precisar recarregar a página.
- Histórico de conversas preservado.
- Indicador de mensagens não lidas.

---

## 4. Busca de Usuários

Para encontrar um jogador específico, use a busca integrada:
- Endpoint AJAX: `/app/message/api/search-users/?q=<username>`
- A busca retorna usuários por nome parcial.

---

## Documentação Relacionada

- 📱 [Rede Social](SOCIAL_USER_GUIDE.md)
- 🔔 [Sistema de Notificações (Técnico)](../notifications/NOTIFICATIONS_README.md)

---

[ Voltar ao Índice](../INDEX.md)

