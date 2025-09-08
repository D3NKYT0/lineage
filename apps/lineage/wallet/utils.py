from django.db import transaction
from .models import *
from .signals import aplicar_transacao
from django.utils.translation import gettext as _
from decimal import Decimal
from .models import Wallet, TransacaoWallet, TransacaoBonus, CoinPurchaseBonus


def calcular_bonus_compra(valor_compra):
    """
    Calcula o bônus aplicável para um valor de compra
    Retorna: (valor_bonus, descricao_bonus, percentual_bonus)
    """
    # Garante que valor_compra seja Decimal
    valor_compra = Decimal(str(valor_compra))
    
    bonus = CoinPurchaseBonus.obter_bonus_para_valor(valor_compra)
    
    if not bonus:
        return Decimal('0.00'), '', Decimal('0.00')
    
    valor_bonus = bonus.calcular_bonus(valor_compra)
    return valor_bonus, bonus.descricao, bonus.bonus_percentual


def aplicar_compra_com_bonus(wallet, valor_compra, metodo_pagamento):
    """
    Aplica uma compra com bônus usando as funções centralizadas
    - Valor da compra vai para saldo normal
    - Bônus vai para saldo_bonus
    Retorna: (valor_total_creditado, valor_bonus, descricao_bonus)
    """
    from .signals import aplicar_transacao, aplicar_transacao_bonus
    
    # Garante que valor_compra seja Decimal
    valor_compra = Decimal(str(valor_compra))
    
    # Calcula o bônus
    valor_bonus, descricao_bonus, percentual_bonus = calcular_bonus_compra(valor_compra)
    
    # Aplica a transação principal na carteira normal
    aplicar_transacao(
        wallet=wallet,
        tipo="ENTRADA",
        valor=valor_compra,
        descricao=f"Compra de moedas via {metodo_pagamento}",
        origem=metodo_pagamento,
        destino=wallet.usuario.username
    )
    
    # Aplica o bônus na carteira de bônus separada
    if valor_bonus > 0:
        aplicar_transacao_bonus(
            wallet=wallet,
            tipo="ENTRADA",
            valor=valor_bonus,
            descricao=f"Bônus: {descricao_bonus}",
            origem="Sistema de Bônus",
            destino=wallet.usuario.username
        )
    
    return valor_compra + valor_bonus, valor_bonus, descricao_bonus


def transferir_para_jogador(wallet_origem, wallet_destino, valor, descricao=""):
    """
    Transfere valor da carteira normal de um jogador para outro
    """
    from .signals import aplicar_transacao
    
    aplicar_transacao(
        wallet=wallet_origem,
        tipo="SAIDA",
        valor=valor,
        descricao=f"Transferência para {wallet_destino.usuario.username}",
        origem=wallet_origem.usuario.username,
        destino=wallet_destino.usuario.username
    )

    aplicar_transacao(
        wallet=wallet_destino,
        tipo="ENTRADA",
        valor=valor,
        descricao=f"Transferência de {wallet_origem.usuario.username}",
        origem=wallet_origem.usuario.username,
        destino=wallet_destino.usuario.username
    )


def transferir_bonus_para_jogador(wallet_origem, wallet_destino, valor, descricao=""):
    """
    Transfere valor da carteira de bônus de um jogador para outro
    """
    from .signals import aplicar_transacao_bonus
    
    aplicar_transacao_bonus(
        wallet=wallet_origem,
        tipo="SAIDA",
        valor=valor,
        descricao=f"Transferência de bônus para {wallet_destino.usuario.username}",
        origem=wallet_origem.usuario.username,
        destino=wallet_destino.usuario.username
    )

    aplicar_transacao_bonus(
        wallet=wallet_destino,
        tipo="ENTRADA",
        valor=valor,
        descricao=f"Transferência de bônus de {wallet_origem.usuario.username}",
        origem=wallet_origem.usuario.username,
        destino=wallet_destino.usuario.username
    )
