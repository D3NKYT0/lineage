from decimal import Decimal
from .models import *
from django.utils.translation import gettext as _


def aplicar_transacao(wallet, tipo, valor, descricao="", origem="", destino=""):
    # Garante que valor seja Decimal
    valor = Decimal(valor)

    if tipo == "SAIDA" and wallet.saldo < valor:
        raise ValueError(_("Saldo insuficiente."))
    
    if tipo == "ENTRADA":
        wallet.saldo += valor
    elif tipo == "SAIDA":
        wallet.saldo -= valor
    
    wallet.save()

    return TransacaoWallet.objects.create(
        wallet=wallet,
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        origem=origem,
        destino=destino
    )


def aplicar_transacao_bonus(wallet, tipo, valor, descricao="", origem="", destino=""):
    # Garante que valor seja Decimal
    valor = Decimal(valor)

    if tipo == "SAIDA" and wallet.saldo_bonus < valor:
        raise ValueError(_("Saldo de bônus insuficiente."))
    
    if tipo == "ENTRADA":
        wallet.saldo_bonus += valor
    elif tipo == "SAIDA":
        wallet.saldo_bonus -= valor
    
    wallet.save()

    return TransacaoBonus.objects.create(
        wallet=wallet,
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        origem=origem,
        destino=destino
    )
