# Guia do Sistema de Helpdesk (Solicitações)

> **Última atualização:** 21/02/2026

## Arquitetura do Helpdesk

O módulo de solicitações foi projetado para atuar como uma central de atendimento ao jogador, garantindo organização via categorização técnica, escalonamento e histórico contínuo (audit trail).

## 🗂️ Sistema de Categorias

Ao preencher o formulário interativo de solicitação, a plataforma subdivide a natureza do problema, permitindo a correta distribuição e filtragem para os Administradores de forma rápida. As categorias principais incluem:
- **Técnico** (Problemas de software/cliente)
- **Faturamento** (MercadoPago/Stripe)
- **Conta** (Restrição/Recuperação)
- **Suporte ao Jogo**
- **Relatório de Bug** e **Solicitação de Funcionalidade**
- **Segurança** e **Performance**

## 🚥 Sistema de Priorização

A escala garante SLA flexível. Cores vibrantes no dashboard auxiliam a visão rápida do peso:
- Baixa (Verde)
- Média (Amarelo)
- Alta (Vermelho Clássico)
- Urgente (Cinza Escuro)
- Crítica (Vermelho Intenso)

## 📌 Mecânica de Status do Ciclo de Vida

Todo ticket inserido é rastreado por um workflow predefinido na interface de staff.
- Abertura padrão no estado **"Aberto"**.
- Movimentações de avaliação como **"Em Andamento"**, **"Aguardando Usuário"** ou **"Aguardando Terceiros"**.
- Finalizações através de **"Resolvido"**, **"Fechado"**, **"Cancelado"** ou **"Rejeitado"**.

## 🛠️ Dashboard do Administrador

A equipe tem acesso a um painel unificado em rotas designadas que não apenas listam todos os tickets agrupados (filtrados via dropdown interactivo e checkboxes), como contam com:
- **Resolução inline**: Mudança de status dentro da leitura do próprio ticket sem recarregar a tela principal.
- **Transbordo**: Atribuição flexível do ticket de um administrador/staffer para outro analista disponível.
- **Histórico de Alterações**: Registro obrigatório de comentários a cada avanço no pipeline, disparando notificações internas de feedback direto para o dispositivo do jogador final.

## 💾 Modelos de Entidade (Django)

- `apps/main/solicitation/models.py`: Centraliza todos os campos cruciais das solicitações customizadas.
- `apps/main/solicitation/choices.py`: Indexa as listas numéricas de escolha (Tuple Constants).
- Os fluxos assíncronos e submissões baseadas em arquivos são tratadas no escopo do `forms.py`.

---

[ Voltar ao Índice](../INDEX.md)

