from .validators import registrar_validador
from django.utils.translation import get_language_from_request

from apps.main.home.models import AddressUser
from apps.main.solicitation.models import Solicitation
from apps.main.message.models import Friendship

from apps.lineage.shop.models import ShopPurchase, Cart
from apps.lineage.auction.models import Bid, Auction
from apps.lineage.payment.models import PedidoPagamento, Pagamento
from apps.lineage.wallet.models import TransacaoWallet
from apps.lineage.inventory.models import InventoryItem, InventoryLog

import time


@registrar_validador('primeiro_login')
def primeiro_login(user, request=None):
    return True  # Apenas logar

@registrar_validador('10_leiloes')
def dez_leiloes(user, request=None):
    return user.auctions.count() >= 10

@registrar_validador('primeira_solicitacao')
def primeira_solicitacao(user, request=None):
    return Solicitation.objects.filter(user=user).exists()

@registrar_validador('avatar_editado')
def avatar_editado(user, request=None):
    return bool(getattr(user, 'avatar', None))

@registrar_validador('endereco_cadastrado')
def endereco(user, request=None):
    return AddressUser.objects.filter(user=user).exists()

@registrar_validador('email_verificado')
def email_verificado(user, request=None):
    return getattr(user, 'is_email_verified', False)

@registrar_validador('2fa_ativado')
def dois_fatores(user, request=None):
    return getattr(user, 'is_2fa_enabled', False)

@registrar_validador('idioma_trocado')
def idioma(user, request=None):
    if not request:
        return False
    idioma = get_language_from_request(request)
    return idioma != 'pt-br'  # ou qualquer padrão

@registrar_validador('primeiro_amigo')
def primeiro_amigo(user, request=None):
    return Friendship.objects.filter(user=user).exists()

@registrar_validador('primeiro_amigo_aceito')
def primeiro_amigo_aceito(user, request=None):
    return Friendship.objects.filter(user=user, accepted=True).exists()

@registrar_validador('primeira_compra')
def primeira_compra(user, request=None):
    return ShopPurchase.objects.filter(user=user).exists()

@registrar_validador('primeiro_lance')
def primeiro_lance(user, request=None):
    return Bid.objects.filter(bidder=user).exists()

@registrar_validador('primeiro_cupom')
def primeiro_cupom(user, request=None):
    return Cart.objects.filter(user=user, promocao_aplicada__isnull=False).exists()

@registrar_validador('primeiro_pedido_pagamento')
def primeiro_pedido_pagamento(user, request=None):
    return PedidoPagamento.objects.filter(usuario=user).exists()

@registrar_validador('primeiro_pagamento_concluido')
def primeiro_pagamento_concluido(user, request=None):
    return Pagamento.objects.filter(usuario=user, status='approved').exists()

@registrar_validador('primeira_transferencia_para_o_jogo')
def primeira_transferencia_para_o_jogo(user, request=None):
    return TransacaoWallet.objects.filter(
        wallet__usuario=user,
        tipo="SAIDA",
        descricao__icontains="Transferência para o servidor"
    ).exists()

@registrar_validador('primeira_transferencia_para_jogador')
def primeira_transferencia_para_jogador(user, request=None):
    return TransacaoWallet.objects.filter(
        wallet__usuario=user,
        tipo="SAIDA",
        descricao__icontains="Transferência para jogador"
    ).exists()

@registrar_validador('primeira_retirada_item')
def primeira_retirada_item(user, request=None):
    return InventoryItem.objects.filter(inventory__user=user).exists()

@registrar_validador('primeira_insercao_item')
def primeira_insercao_item(user, request=None):
    return InventoryLog.objects.filter(user=user, acao='INSERIU_NO_JOGO').exists()

@registrar_validador('primeira_troca_itens')
def primeira_troca_itens(user, request=None):
    return InventoryLog.objects.filter(user=user, acao='TROCA_ENTRE_PERSONAGENS').exists()

@registrar_validador('nivel_10')
def nivel_10(user, request=None):
    try:
        perfil = user.perfilgamer
        return perfil.level >= 10
    except:
        return False

@registrar_validador('50_lances')
def cinquenta_lances(user, request=None):
    return Bid.objects.filter(bidder=user).count() >= 50

@registrar_validador('primeiro_vencedor_leilao')
def primeiro_vencedor_leilao(user, request=None):
    return Auction.objects.filter(highest_bidder=user, status='finished').exists()

@registrar_validador('1000_xp')
def mil_xp(user, request=None):
    try:
        perfil = user.perfilgamer
        # Calcula XP total acumulado
        xp_total = perfil.xp
        level_atual = perfil.level
        
        # Adiciona XP de todos os níveis anteriores
        for nivel in range(1, level_atual):
            xp_total += 100 + (nivel - 1) * 25
            
        return xp_total >= 1000
    except:
        return False

@registrar_validador('100_transacoes')
def cem_transacoes(user, request=None):
    from apps.lineage.wallet.models import TransacaoWallet, TransacaoBonus
    # Conta transações normais e de bônus
    transacoes_normais = TransacaoWallet.objects.filter(wallet__usuario=user).count()
    transacoes_bonus = TransacaoBonus.objects.filter(wallet__usuario=user).count()
    return (transacoes_normais + transacoes_bonus) >= 100

@registrar_validador('primeiro_bonus')
def primeiro_bonus(user, request=None):
    from apps.lineage.wallet.models import TransacaoBonus
    return TransacaoBonus.objects.filter(wallet__usuario=user, tipo='ENTRADA').exists()

@registrar_validador('nivel_25')
def nivel_25(user, request=None):
    try:
        perfil = user.perfilgamer
        return perfil.level >= 25
    except:
        return False

@registrar_validador('primeira_solicitacao_resolvida')
def primeira_solicitacao_resolvida(user, request=None):
    from apps.main.solicitation.models import Solicitation
    return Solicitation.objects.filter(user=user, status='closed').exists()

# =========================== NOVAS CONQUISTAS CRIATIVAS ===========================

@registrar_validador('colecionador_itens')
def colecionador_itens(user, request=None):
    """Possui 10 ou mais itens no inventário"""
    return InventoryItem.objects.filter(inventory__user=user).count() >= 10

@registrar_validador('mestre_inventario')
def mestre_inventario(user, request=None):
    """Possui 50 ou mais itens no inventário"""
    return InventoryItem.objects.filter(inventory__user=user).count() >= 50

@registrar_validador('trocador_incansavel')
def trocador_incansavel(user, request=None):
    """Realizou 10 ou mais trocas de itens"""
    return InventoryLog.objects.filter(user=user, acao='TROCA_ENTRE_PERSONAGENS').count() >= 10

@registrar_validador('gerenciador_economico')
def gerenciador_economico(user, request=None):
    """Realizou 20 ou mais transferências para o jogo"""
    return TransacaoWallet.objects.filter(
        wallet__usuario=user,
        tipo="SAIDA",
        descricao__icontains="Transferência para o servidor"
    ).count() >= 20

@registrar_validador('benfeitor_comunitario')
def benfeitor_comunitario(user, request=None):
    """Realizou 10 ou mais transferências para outros jogadores"""
    return TransacaoWallet.objects.filter(
        wallet__usuario=user,
        tipo="SAIDA",
        descricao__icontains="Transferência para jogador"
    ).count() >= 10

@registrar_validador('bonus_diario_7dias')
def bonus_diario_7dias(user, request=None):
    """Recebeu bônus diário por 7 dias consecutivos"""
    from apps.lineage.wallet.models import TransacaoBonus
    from datetime import datetime, timedelta
    
    # Verifica se recebeu bônus nos últimos 7 dias
    data_limite = datetime.now() - timedelta(days=7)
    bonus_recentes = TransacaoBonus.objects.filter(
        wallet__usuario=user,
        tipo='ENTRADA',
        descricao__icontains="Bônus diário",
        created_at__gte=data_limite
    ).count()
    return bonus_recentes >= 7

@registrar_validador('bonus_diario_30dias')
def bonus_diario_30dias(user, request=None):
    """Recebeu bônus diário por 30 dias consecutivos"""
    from apps.lineage.wallet.models import TransacaoBonus
    from datetime import datetime, timedelta
    
    data_limite = datetime.now() - timedelta(days=30)
    bonus_recentes = TransacaoBonus.objects.filter(
        wallet__usuario=user,
        tipo='ENTRADA',
        descricao__icontains="Bônus diário",
        created_at__gte=data_limite
    ).count()
    return bonus_recentes >= 30

@registrar_validador('patrocinador_ouro')
def patrocinador_ouro(user, request=None):
    """Realizou 5 ou mais pagamentos aprovados"""
    return Pagamento.objects.filter(usuario=user, status='approved').count() >= 5

@registrar_validador('patrocinador_diamante')
def patrocinador_diamante(user, request=None):
    """Realizou 10 ou mais pagamentos aprovados"""
    return Pagamento.objects.filter(usuario=user, status='approved').count() >= 10

@registrar_validador('comprador_frequente')
def comprador_frequente(user, request=None):
    """Realizou 5 ou mais compras na loja"""
    return ShopPurchase.objects.filter(user=user).count() >= 5

@registrar_validador('comprador_vip')
def comprador_vip(user, request=None):
    """Realizou 15 ou mais compras na loja"""
    return ShopPurchase.objects.filter(user=user).count() >= 15

@registrar_validador('leiloeiro_profissional')
def leiloeiro_profissional(user, request=None):
    """Criou 25 ou mais leilões"""
    return user.auctions.count() >= 25

@registrar_validador('leiloeiro_mestre')
def leiloeiro_mestre(user, request=None):
    """Criou 50 ou mais leilões"""
    return user.auctions.count() >= 50

@registrar_validador('lanceador_profissional')
def lanceador_profissional(user, request=None):
    """Realizou 100 ou mais lances"""
    return Bid.objects.filter(bidder=user).count() >= 100

@registrar_validador('lanceador_mestre')
def lanceador_mestre(user, request=None):
    """Realizou 200 ou mais lances"""
    return Bid.objects.filter(bidder=user).count() >= 200

@registrar_validador('vencedor_serie')
def vencedor_serie(user, request=None):
    """Venceu 3 ou mais leilões"""
    return Auction.objects.filter(highest_bidder=user, status='finished').count() >= 3

@registrar_validador('vencedor_mestre')
def vencedor_mestre(user, request=None):
    """Venceu 10 ou mais leilões"""
    return Auction.objects.filter(highest_bidder=user, status='finished').count() >= 10

@registrar_validador('cupom_mestre')
def cupom_mestre(user, request=None):
    """Aplicou 5 ou mais cupons promocionais"""
    return Cart.objects.filter(user=user, promocao_aplicada__isnull=False).count() >= 5

@registrar_validador('cupom_expert')
def cupom_expert(user, request=None):
    """Aplicou 15 ou mais cupons promocionais"""
    return Cart.objects.filter(user=user, promocao_aplicada__isnull=False).count() >= 15

@registrar_validador('solicitante_frequente')
def solicitante_frequente(user, request=None):
    """Abriu 5 ou mais solicitações de suporte"""
    return Solicitation.objects.filter(user=user).count() >= 5

@registrar_validador('solicitante_expert')
def solicitante_expert(user, request=None):
    """Abriu 15 ou mais solicitações de suporte"""
    return Solicitation.objects.filter(user=user).count() >= 15

@registrar_validador('resolvedor_problemas')
def resolvedor_problemas(user, request=None):
    """Teve 3 ou mais solicitações resolvidas"""
    return Solicitation.objects.filter(user=user, status='closed').count() >= 3

@registrar_validador('resolvedor_mestre')
def resolvedor_mestre(user, request=None):
    """Teve 10 ou mais solicitações resolvidas"""
    return Solicitation.objects.filter(user=user, status='closed').count() >= 10

@registrar_validador('rede_social')
def rede_social(user, request=None):
    """Tem 5 ou mais amigos aceitos"""
    return Friendship.objects.filter(user=user, accepted=True).count() >= 5

@registrar_validador('rede_social_mestre')
def rede_social_mestre(user, request=None):
    """Tem 15 ou mais amigos aceitos"""
    return Friendship.objects.filter(user=user, accepted=True).count() >= 15

@registrar_validador('nivel_50')
def nivel_50(user, request=None):
    """Alcançou o nível 50 no sistema"""
    try:
        perfil = user.perfilgamer
        return perfil.level >= 50
    except:
        return False

@registrar_validador('nivel_75')
def nivel_75(user, request=None):
    """Alcançou o nível 75 no sistema"""
    try:
        perfil = user.perfilgamer
        return perfil.level >= 75
    except:
        return False

@registrar_validador('nivel_100')
def nivel_100(user, request=None):
    """Alcançou o nível 100 no sistema"""
    try:
        perfil = user.perfilgamer
        return perfil.level >= 100
    except:
        return False

@registrar_validador('5000_xp')
def cinco_mil_xp(user, request=None):
    """Acumulou 5000 pontos de experiência"""
    try:
        perfil = user.perfilgamer
        xp_total = perfil.xp
        level_atual = perfil.level
        
        for nivel in range(1, level_atual):
            xp_total += 100 + (nivel - 1) * 25
            
        return xp_total >= 5000
    except:
        return False

@registrar_validador('10000_xp')
def dez_mil_xp(user, request=None):
    """Acumulou 10000 pontos de experiência"""
    try:
        perfil = user.perfilgamer
        xp_total = perfil.xp
        level_atual = perfil.level
        
        for nivel in range(1, level_atual):
            xp_total += 100 + (nivel - 1) * 25
            
        return xp_total >= 10000
    except:
        return False

@registrar_validador('250_transacoes')
def duzentos_cinquenta_transacoes(user, request=None):
    """Realizou 250 transações na carteira"""
    from apps.lineage.wallet.models import TransacaoWallet, TransacaoBonus
    transacoes_normais = TransacaoWallet.objects.filter(wallet__usuario=user).count()
    transacoes_bonus = TransacaoBonus.objects.filter(wallet__usuario=user).count()
    return (transacoes_normais + transacoes_bonus) >= 250

@registrar_validador('500_transacoes')
def quinhentas_transacoes(user, request=None):
    """Realizou 500 transações na carteira"""
    from apps.lineage.wallet.models import TransacaoWallet, TransacaoBonus
    transacoes_normais = TransacaoWallet.objects.filter(wallet__usuario=user).count()
    transacoes_bonus = TransacaoBonus.objects.filter(wallet__usuario=user).count()
    return (transacoes_normais + transacoes_bonus) >= 500

@registrar_validador('bonus_mestre')
def bonus_mestre(user, request=None):
    """Recebeu 10 ou mais bônus"""
    from apps.lineage.wallet.models import TransacaoBonus
    return TransacaoBonus.objects.filter(wallet__usuario=user, tipo='ENTRADA').count() >= 10

@registrar_validador('bonus_expert')
def bonus_expert(user, request=None):
    """Recebeu 25 ou mais bônus"""
    from apps.lineage.wallet.models import TransacaoBonus
    return TransacaoBonus.objects.filter(wallet__usuario=user, tipo='ENTRADA').count() >= 25
