# Guia Prático de Moderação

> **Última atualização:** 21/02/2026

O PDL conta com canais de moderação que englobam isolamento de contas no jogo (L2J), exclusões do banco no painel Web e moderação passiva da rede social. Este guia orienta o Administrador neste ecossistema.

## 🛡️ Moderação de Conteúdo (Rede Social)

No menu de **Admin do Social**, o Staff tem permissão global de exclusão (Delete) de Postagens ofensivas, falsas ou que infrinjam a política do servidor.
1. Localize a publicação ofensiva e remova-a (seja via ID da postagem na URL administrativa ou buscando o dono da conta).
2. Para acompanhamentos drásticos, utilize as ferramentas de edição da Conta do Usuário, que podem silenciar (Mute) as postagens e restringir o comportamento social sem barrar acesso ao jogo.

## ⚖️ Banimentos Globais (L2J vs PDL)

Existem duas esferas punitivas:

1. **Banir a Conta Principal (Web/Dashboard)**: A conta Master que gerecia as credenciais, o mercado e o suporte é paralisada.
2. **Banir a sub-conta (Personagens L2J)**: Ferramentas associadas ao app de L2J permitem sinalizar flag de Access Level negativo diretamente nos logins de base do Lineage, derrubando o login no Client instantaneamente.

### Como Enviar Avisos Sistêmicos?
Em vez de banimentos frios, utilize o disparador central em **Notificações Globais**: Emita comunicados Flutuantes ou no Inbox para alertar clãs de que estão sendo observados pela gerência do servidor.

## 📄 Exportando Logs para Auditoria

Membros da Staff podem extrair a prova irrefutável de transações financeiras, auditoria administrativa e de tickets excluídos utilizando os utilitários de Moderação listados no sistema.
Verifique o pipeline de auditoria via `docker-compose exec` seguindo o guia avançado `docs/moderation/EXPORT_MODERATION_LOGS.md` caso necessite embasar ações criminosas (Ex: Fraude de Mercado Pago ou Chargeback de Cartões de Crédito).

---

[ Voltar ao Índice](../INDEX.md)

