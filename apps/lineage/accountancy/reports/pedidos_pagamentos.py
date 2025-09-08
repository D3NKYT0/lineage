from apps.lineage.payment.models import PedidoPagamento, Pagamento


def pedidos_pagamentos_resumo():
    pedidos = PedidoPagamento.objects.all().order_by('-data_criacao')
    relatorio = []

    # Mapeamento de status do modelo para o template
    status_mapping = {
        'CONFIRMADO': 'aprovado',
        'PENDENTE': 'pendente',
        'FALHOU': 'cancelado',
        'PROCESSANDO': 'processando',
    }

    # Mapeamento de métodos de pagamento
    metodo_mapping = {
        'MercadoPago': 'pix',  # MercadoPago geralmente usa PIX
        'Stripe': 'cartao',    # Stripe geralmente usa cartão
        'PIX': 'pix',
        'CARTAO': 'cartao',
        'BOLETO': 'boleto',
    }

    for pedido in pedidos:
        pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()
        
        # Determina o status para exibição
        status_pedido = status_mapping.get(pedido.status, pedido.status.lower())
        
        # Determina o método de pagamento para exibição
        metodo_pagamento = metodo_mapping.get(pedido.metodo, pedido.metodo.lower())
        
        relatorio.append({
            'id_pedido': pedido.id,                    # Corrigido para 'id_pedido'
            'usuario': pedido.usuario.username,
            'valor': pedido.valor_pago,                 # Corrigido para 'valor'
            'bonus_aplicado': pedido.bonus_aplicado,    # Adicionado informação de bônus
            'total_creditado': pedido.total_creditado,  # Adicionado total creditado
            'status': status_pedido,                    # Corrigido para 'status'
            'metodo_pagamento': metodo_pagamento,       # Corrigido para 'metodo_pagamento'
            'data': pedido.data_criacao,
        })

    return relatorio
