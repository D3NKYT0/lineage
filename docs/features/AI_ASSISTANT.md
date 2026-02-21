# Documentação: Assistente Virtual de Inteligência Artificial

> **Última atualização:** 20/02/2026

O sub-módulo IA fornece uma interface avançada de chat interativo construído em formato de pré-atendimento inteligente (suporte "Nível 0"). Baseado nos modelos da Anthropic (Claude), ele desvia chamados rotineiros cruzando perguntas com os FAQs públicos para oferecer soluções instantâneas antes do usuário abrir uma "Solicitação Formal".

## 🤖 Operações e Comportamento

O bot funciona num fluxo conversacional restrito:
- **Identificação Dinâmica**: Cada sessão gerada e persistida está obrigatoriamente vinculada à autenticação do usuário, permitindo o histórico recorrente, continuidade conversacional e prevenção a spans anônimos.
- **Cruzamento Semântico**: A AI avalia, antes de enviar sua resposta final, se o diálogo aborda temas técnicos crônicos e sugere com um payload estruturado ao jogador a criação automatizada do ticket de Suporte contendo Título, Categoria e Prioridade adequados. 
- **Base de Conhecimento**: Alimenta a AI automaticamente com até 20 instâncias limitadas das perguntas mais acessadas registradas pelo App de FAQ da administração. O modelo aceita interpretação multilinguística (PT/EN/ES).

## 📡 Engenharia de Redes (WebSockets)

A arquitetura usa comunicação Real-Time (Duplex):
- Implementação baseada em `AuthMiddlewareStack` do **Django Channels**. Acompanhada com suporte transparente a Typing Indicators front-end (JavaScript).
- Endpoint reservado `/ws/chatbot/` que transita estritamente conexões com sessões válidas (Consumer Auth). Os protocolos e rotas configuram-se através do respectivo `routing.py`.

## 💾 Modelagem de Banco

Todo tráfego é arquivado para auditoria técnica sob contexto das limitações de tokenização:
- `ChatSession`: Mantém a macro-entidade ativa rastreada sobre IDs em strings dinâmicas (Títulos auto-gerenciados pela interação). Ligações ManyToOne caso a sessão derive para uma Solicitação física.
- `ChatMessage`: Armazenamento binário categorizando papéis de conversa de LLMs (system, assistant, user). Conta ativamente os arrays de payload, como volume de tokens utilizado e links de metadados retornados da API original (Analytics de Custo no Admin).

## 🛠️ Detalhes de Configuração do Ambiente

1. A engine requer a chave principal de provedor registrada no container `.env`:
   ```env
   ANTHROPIC_API_KEY=sua_chave_secreta_aqui
   ```
2. Custo Monetário: Devido às chamadas sequenciais síncronas HTTP por mensagem, os endpoints disparam de forma custosa e em larga escala requerem instâncias de `Celery` para workers async ou mudança de motor para modelos low-tier (como o `haiku` default). O acompanhamento dos limites de gasto pode ser visto direto pelos painéis unificados nativos dos logs do bot no Django Administration (`/admin/ai_assistant/`).
