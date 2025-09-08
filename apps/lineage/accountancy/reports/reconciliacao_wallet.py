from apps.lineage.wallet.models import Wallet, TransacaoWallet
from django.db.models import Sum
from django.utils import timezone


def reconciliacao_wallet_transacoes():
    wallets = Wallet.objects.all()
    relatorio = []

    for wallet in wallets:
        # Calcula totais de transações
        total_entradas = TransacaoWallet.objects.filter(wallet=wallet, tipo='ENTRADA').aggregate(total=Sum('valor'))['total'] or 0
        total_saidas = TransacaoWallet.objects.filter(wallet=wallet, tipo='SAIDA').aggregate(total=Sum('valor'))['total'] or 0
        
        # Conta número de transações
        num_transacoes = TransacaoWallet.objects.filter(wallet=wallet).count()

        saldo_calculado = total_entradas - total_saidas
        diferenca = wallet.saldo - saldo_calculado
        
        # Determina o status baseado na diferença
        if diferenca == 0:
            status = 'reconciliado'
        elif abs(diferenca) <= 0.01:  # Tolerância de 1 centavo
            status = 'reconciliado'
        elif abs(diferenca) <= 1.00:  # Tolerância de 1 real
            status = 'em_analise'
        else:
            status = 'discrepancia'

        relatorio.append({
            'usuario': wallet.usuario.username,
            'saldo_wallet': wallet.saldo,
            'saldo_banco': saldo_calculado,        # Corrigido para 'saldo_banco'
            'diferenca': diferenca,
            'status': status,                      # Adicionado campo status
            'ultima_verificacao': timezone.now(),  # Adicionado timestamp
            'num_transacoes': num_transacoes,      # Adicionado número de transações
        })

    return relatorio
