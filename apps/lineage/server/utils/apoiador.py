from apps.lineage.server.models import Apoiador, Comissao
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import TransacaoWallet
from decimal import Decimal
from apps.lineage.shop.models import ShopPurchase, PromotionCode
from django.db.models import Sum


def pagar_comissao(apoiador: Apoiador, valor_solicitado: Decimal):
    # Tenta pegar o cupom ativo do apoiador
    try:
        cupom = PromotionCode.objects.get(apoiador=apoiador, ativo=True)
        percentual_comissao = cupom.desconto_percentual
    except PromotionCode.DoesNotExist:
        return  # Se não houver cupom ativo, sai da função

    # Pega todas as compras não pagas associadas ao apoiador
    todas_as_compras = ShopPurchase.objects.filter(apoiador=apoiador)

    # Se não houver compras não pagas, não faz nada
    if not todas_as_compras:
        return

    # Para cada compra não paga, calcula e registra a comissão
    for compra in todas_as_compras:
        # Calcula o valor da comissão para esta compra
        valor_comissao = (compra.total_pago * percentual_comissao) / Decimal('100')

        # Cria a comissão para a compra com o valor calculado
        comissao = Comissao.objects.create(
            apoiador=apoiador,
            compra=compra,
            valor=valor_comissao,
            pago=True  # Marca como pago
        )

    # Atualiza a carteira do apoiador
    wallet, created = Wallet.objects.get_or_create(usuario=apoiador.user)
    wallet.saldo += valor_solicitado
    wallet.save()

    # Registra a transação na carteira
    TransacaoWallet.objects.create(
        wallet=wallet,
        tipo='ENTRADA',
        valor=valor_solicitado,
        descricao='Comissão por venda',
        origem='Sistema',
        destino=apoiador.nome_publico
    )


def calcular_valor_disponivel(apoiador):
    # Tentar pegar o cupom ativo do apoiador
    try:
        cupom = PromotionCode.objects.get(apoiador=apoiador, ativo=True)
        percentual_comissao = cupom.desconto_percentual
    except PromotionCode.DoesNotExist:
        return Decimal('0.00')

    # Total de vendas associadas ao apoiador (com tratamento de None)
    total_das_compras = ShopPurchase.objects.filter(apoiador=apoiador)
    total_vendas = total_das_compras.aggregate(
        total=Sum('total_pago')
    )['total'] or Decimal('0.00')

    # Calcular comissão gerada com base nas vendas e no percentual do cupom
    comissao_gerada = (total_vendas * percentual_comissao) / Decimal('100')

    # Total já pago (comissões já pagas)
    total_pago = Comissao.objects.filter(
        apoiador=apoiador,
        pago=True
    ).aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0.00')

    # Valor disponível é a comissão gerada menos o total já pago
    valor_disponivel = comissao_gerada - total_pago

    # Garantir que o valor disponível nunca seja negativo
    return max(valor_disponivel, Decimal('0.00'))
