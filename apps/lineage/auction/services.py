import logging
from django.db import transaction
from django.utils.translation import gettext as _
from django.urls import reverse

from core.log_utils import log_action
from .models import Bid

logger = logging.getLogger(__name__)
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory
from apps.lineage.auction.models import Auction
from utils.push import send_push_for_event, EVENT_LEILAO_VENDIDO, EVENT_LEILAO_GANHO


@transaction.atomic
def place_bid(auction, bidder, bid_amount, character_name):
    if auction.seller == bidder:
        raise ValueError(_("Você não pode dar lances no seu próprio leilão."))

    if not auction.is_active:
        raise ValueError(_("Leilão encerrado."))

    if bid_amount <= auction.starting_bid:
        raise ValueError(_("O lance deve ser maior que o valor inicial."))

    if auction.current_bid and bid_amount <= auction.current_bid:
        raise ValueError(_("O lance deve ser maior que o lance atual."))

    wallet, created = Wallet.objects.get_or_create(usuario=bidder)

    if wallet.saldo < bid_amount:
        raise ValueError(_("Saldo insuficiente."))

    # Devolve o valor do último lance ao último usuário
    if auction.highest_bidder:
        try:
            old_wallet = Wallet.objects.select_for_update().get(usuario=auction.highest_bidder)
        except Wallet.DoesNotExist:
            old_wallet = Wallet.objects.create(usuario=auction.highest_bidder)

        aplicar_transacao(
            old_wallet,
            'ENTRADA',
            auction.current_bid,
            _("Devolução de lance no leilão"),
            origem=_("Leilão")
        )

    # Desconta o valor do novo lance
    aplicar_transacao(
        wallet,
        'SAIDA',
        bid_amount,
        _("Lance no leilão"),
        destino=str(auction.seller)
    )

    auction.current_bid = bid_amount
    auction.highest_bidder = bidder
    auction.save()

    bid = Bid.objects.create(
        auction=auction,
        bidder=bidder,
        amount=bid_amount,
        character_name=character_name
    )
    log_action(
        logger, "auction_lance", "sucesso",
        auction_id=auction.id,
        bidder=bidder.username,
        amount=str(bid_amount),
        character_name=character_name,
    )
    return bid


@transaction.atomic
def finish_auction(auction: Auction):
    if auction.is_active:
        raise ValueError(_("Leilão ainda está ativo."))

    if auction.highest_bidder:
        # Transfere o dinheiro para o vendedor
        seller_wallet, created = Wallet.objects.get_or_create(usuario=auction.seller)
        aplicar_transacao(
            seller_wallet,
            'ENTRADA',
            auction.current_bid,
            _("Venda no leilão #%d") % auction.id,
            origem=str(auction.highest_bidder)
        )

        winning_bid = auction.bids.order_by('-amount', '-created_at').first()
        if not winning_bid:
            raise ValueError(_("Não foi possível determinar o lance vencedor."))
        log_action(
            logger, "auction_finalizado", "venda",
            auction_id=auction.id,
            seller=auction.seller.username,
            winner=auction.highest_bidder.username,
            amount=str(auction.current_bid),
        )

        dest_inventory = Inventory.objects.get(
            user=auction.highest_bidder,
            character_name=winning_bid.character_name
        )

        dest_item, created = InventoryItem.objects.get_or_create(
            inventory=dest_inventory,
            item_id=auction.item_id,
            enchant=auction.item_enchant,
            defaults={
                'quantity': auction.quantity,
                'item_name': auction.item_name,
            }
        )

        if not created:
            dest_item.quantity += auction.quantity
            dest_item.save()

        # Marca o leilão como finalizado e pago
        auction.status = 'finished'
        auction.save()

        # Push: vendedor (item vendido) e comprador (você ganhou)
        url_leiloes = reverse('auction:listar_leiloes')
        send_push_for_event(
            auction.seller,
            EVENT_LEILAO_VENDIDO,
            url=url_leiloes,
            item_name=auction.item_name or str(auction.item_id),
            async_send=True,
        )
        send_push_for_event(
            auction.highest_bidder,
            EVENT_LEILAO_GANHO,
            url=url_leiloes,
            item_name=auction.item_name or str(auction.item_id),
            async_send=True,
        )

    else:
        # Se ninguém comprou, devolve o item ao vendedor
        seller_inventory = Inventory.objects.get(
            user=auction.seller,
            character_name=auction.character_name
        )

        returned_item, created = InventoryItem.objects.get_or_create(
            inventory=seller_inventory,
            item_id=auction.item_id,
            enchant=auction.item_enchant,
            defaults={'item_name': auction.item_name, 'quantity': auction.quantity}
        )

        if not created:
            returned_item.quantity += auction.quantity
            returned_item.save()

        # Marca como expirado
        auction.status = 'finished'
        auction.save()
