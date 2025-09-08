from apps.lineage.wallet.models import TransacaoWallet
from django.db.models import Sum
from django.db.models.functions import TruncDate

def fluxo_caixa_por_dia():
    # Renomeando a anotação para evitar conflito com o campo 'data'
    transacoes = TransacaoWallet.objects.annotate(data_truncada=TruncDate('data'))

    entradas = transacoes.filter(tipo='ENTRADA').values('data_truncada').annotate(
        total=Sum('valor')
    ).order_by('-data_truncada')

    saidas = transacoes.filter(tipo='SAIDA').values('data_truncada').annotate(
        total=Sum('valor')
    ).order_by('-data_truncada')

    # Junta os dados por data
    dias = {}
    for entrada in entradas:
        dias[entrada['data_truncada']] = {
            'entrada': entrada['total'],
            'saida': 0
        }

    for saida in saidas:
        if saida['data_truncada'] in dias:
            dias[saida['data_truncada']]['saida'] = saida['total']
        else:
            dias[saida['data_truncada']] = {
                'entrada': 0,
                'saida': saida['total']
            }

    # Converte pra lista ordenada por data decrescente
    relatorio = []
    for data, valores in sorted(dias.items(), reverse=True):
        saldo = valores['entrada'] - valores['saida']
        
        # Determina a tendência baseada no saldo
        if saldo > 0:
            tendencia = 'positiva'
        elif saldo < 0:
            tendencia = 'negativa'
        else:
            tendencia = 'estavel'
        
        relatorio.append({
            'data': data,
            'entradas': valores['entrada'],  # Corrigido para plural
            'saidas': valores['saida'],      # Corrigido para plural
            'saldo': saldo,
            'tendencia': tendencia           # Adicionado campo que estava faltando
        })

    return relatorio
