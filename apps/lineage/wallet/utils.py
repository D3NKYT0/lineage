import logging
from decimal import Decimal
from django.db import transaction
from django.utils.translation import gettext as _

from core.log_utils import log_action
from .models import Wallet, TransacaoWallet, TransacaoBonus, CoinPurchaseBonus
from .signals import aplicar_transacao

logger = logging.getLogger(__name__)


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


def aplicar_compra_com_bonus(wallet, valor_compra, metodo_pagamento, descricao_extra: str | None = None):
    """
    Aplica uma compra com bônus usando as funções centralizadas
    - Valor da compra vai para saldo normal
    - Bônus vai para saldo_bonus
    Retorna: (valor_total_creditado, valor_bonus, descricao_bonus)
    """
    from .signals import aplicar_transacao, aplicar_transacao_bonus

    valor_compra = Decimal(str(valor_compra))
    valor_bonus, descricao_bonus, percentual_bonus = calcular_bonus_compra(valor_compra)

    descricao_base = f"Compra de moedas via {metodo_pagamento}"
    if descricao_extra:
        descricao_base = f"{descricao_base} {descricao_extra}"

    aplicar_transacao(
        wallet=wallet,
        tipo="ENTRADA",
        valor=valor_compra,
        descricao=descricao_base,
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

    log_action(
        logger, "wallet_compra_moedas", "sucesso",
        username=wallet.usuario.username,
        valor_compra=str(valor_compra),
        valor_bonus=str(valor_bonus),
        metodo=metodo_pagamento,
    )
    return valor_compra + valor_bonus, valor_bonus, descricao_bonus


def transferir_para_jogador(wallet_origem, wallet_destino, valor, descricao=""):
    """
    Transfere valor da carteira normal de um jogador para outro
    """
    from .signals import aplicar_transacao
    from .models import Wallet
    
    # Usa transação atômica para garantir que ambas operações ocorram ou nenhuma
    with transaction.atomic():
        # Bloqueia ambas as carteiras para prevenir race conditions
        wallet_origem = Wallet.objects.select_for_update().get(id=wallet_origem.id)
        wallet_destino = Wallet.objects.select_for_update().get(id=wallet_destino.id)
        
        if wallet_origem.saldo < valor:
            log_action(
                logger, "wallet_transfer_p2p", "saldo_insuficiente",
                remetente=wallet_origem.usuario.username,
                destinatario=wallet_destino.usuario.username,
                valor=str(valor),
                saldo_origem=str(wallet_origem.saldo),
            )
            raise ValueError("Saldo insuficiente.")

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
    log_action(
        logger, "wallet_transfer_p2p", "sucesso",
        remetente=wallet_origem.usuario.username,
        destinatario=wallet_destino.usuario.username,
        valor=str(valor),
    )


def transferir_bonus_para_jogador(wallet_origem, wallet_destino, valor, descricao=""):
    """
    Transfere valor da carteira de bônus de um jogador para outro
    """
    from .signals import aplicar_transacao_bonus
    from .models import Wallet
    
    # Usa transação atômica para garantir que ambas operações ocorram ou nenhuma
    with transaction.atomic():
        # Bloqueia ambas as carteiras para prevenir race conditions
        wallet_origem = Wallet.objects.select_for_update().get(id=wallet_origem.id)
        wallet_destino = Wallet.objects.select_for_update().get(id=wallet_destino.id)
        
        if wallet_origem.saldo_bonus < valor:
            log_action(
                logger, "wallet_transfer_bonus_p2p", "saldo_bonus_insuficiente",
                remetente=wallet_origem.usuario.username,
                destinatario=wallet_destino.usuario.username,
                valor=str(valor),
                saldo_bonus_origem=str(wallet_origem.saldo_bonus),
            )
            raise ValueError("Saldo de bônus insuficiente.")

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
    log_action(
        logger, "wallet_transfer_bonus_p2p", "sucesso",
        remetente=wallet_origem.usuario.username,
        destinatario=wallet_destino.usuario.username,
        valor=str(valor),
    )
