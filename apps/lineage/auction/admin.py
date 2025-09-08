from django.contrib import admin
from .models import Auction, Bid
from core.admin import BaseModelAdmin


@admin.register(Auction)
class AuctionAdmin(BaseModelAdmin):
    list_display = ('item_name', 'seller', 'starting_bid', 'current_bid', 'highest_bidder', 'end_time', 'status', 'is_currently_active')
    list_filter = ('seller', 'status', 'end_time')
    search_fields = ('item_name', 'seller__username', 'highest_bidder__username')
    readonly_fields = ('current_bid', 'highest_bidder')

    def is_currently_active(self, obj):
        from django.utils import timezone
        now = timezone.now()
        return obj.status == 'pending' and obj.end_time > now
    is_currently_active.boolean = True
    is_currently_active.short_description = "Está Ativo?"


@admin.register(Bid)
class BidAdmin(BaseModelAdmin):
    list_display = ('auction', 'bidder', 'amount', 'created_at')
    list_filter = ('bidder', 'created_at')
    search_fields = ('auction__item_name', 'bidder__username')  # Usando item_name diretamente
