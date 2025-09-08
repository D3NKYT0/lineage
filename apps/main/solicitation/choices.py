# Status para sistema de helpdesk
STATUS_CHOICES = [
    ('open', 'Aberto'),
    ('pending', 'Pendente'),
    ('in_progress', 'Em Andamento'),
    ('waiting_user', 'Aguardando Usuário'),
    ('waiting_third_party', 'Aguardando Terceiros'),
    ('resolved', 'Resolvido'),
    ('closed', 'Fechado'),
    ('cancelled', 'Cancelado'),
    ('rejected', 'Rejeitado'),
]

# Categorias para organizar as solicitações
CATEGORY_CHOICES = [
    ('technical', 'Técnico'),
    ('billing', 'Faturamento'),
    ('account', 'Conta'),
    ('game_support', 'Suporte ao Jogo'),
    ('bug_report', 'Relatório de Bug'),
    ('feature_request', 'Solicitação de Funcionalidade'),
    ('general', 'Geral'),
    ('security', 'Segurança'),
    ('performance', 'Performance'),
    ('other', 'Outros'),
]

# Prioridades para as solicitações
PRIORITY_CHOICES = [
    ('low', 'Baixa'),
    ('medium', 'Média'),
    ('high', 'Alta'),
    ('urgent', 'Urgente'),
    ('critical', 'Crítica'),
]
