from apps.lineage.wallet.models import Wallet, TransacaoWallet
from django.db.models import Sum, Count, Max


def saldo_usuario(usuario):
    try:
        wallet = Wallet.objects.get(usuario=usuario)
        saldo_wallet = wallet.saldo
        saldo_bonus = wallet.saldo_bonus
    except Wallet.DoesNotExist:
        return {
            'saldo_wallet': 0,
            'saldo_bonus': 0,
            'saldo_calculado': 0,
            'diferenca': 0,
            'num_transacoes': 0,
            'ultima_transacao': None,
            'status': 'sem_carteira'
        }

    # Calcula totais de transações
    entradas = TransacaoWallet.objects.filter(
        wallet=wallet, tipo='ENTRADA'
    ).aggregate(total=Sum('valor'))['total'] or 0

    saidas = TransacaoWallet.objects.filter(
        wallet=wallet, tipo='SAIDA'
    ).aggregate(total=Sum('valor'))['total'] or 0

    # Conta número de transações e pega a última
    transacoes_info = TransacaoWallet.objects.filter(wallet=wallet).aggregate(
        total=Count('id'),
        ultima=Max('data')
    )

    saldo_calculado = entradas - saidas
    diferenca = saldo_wallet - saldo_calculado
    
    # Determina o status baseado na diferença
    if diferenca == 0:
        status = 'consistente'
    elif abs(diferenca) <= 0.01:  # Tolerância de 1 centavo
        status = 'consistente'
    elif abs(diferenca) <= 1.00:  # Tolerância de 1 real
        status = 'pequena_discrepancia'
    else:
        status = 'discrepancia'

    return {
        'saldo_wallet': saldo_wallet,
        'saldo_bonus': saldo_bonus,
        'saldo_calculado': saldo_calculado,
        'diferenca': diferenca,
        'num_transacoes': transacoes_info['total'],
        'ultima_transacao': transacoes_info['ultima'],
        'status': status
    }
