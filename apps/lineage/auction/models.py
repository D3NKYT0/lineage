from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel
from .choices import STATUS_CHOICES


class Auction(BaseModel):
    item_id = models.IntegerField(null=True, blank=True, verbose_name=_("Item ID"))
    item_name = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Item Name"))
    item_enchant = models.IntegerField(default=0, verbose_name=_("Item Enchant"))
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Quantity"))
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auctions', verbose_name=_("Seller"))
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Starting Bid"))
    current_bid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_("Current Bid"))
    highest_bidder = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bids', verbose_name=_("Highest Bidder"))
    end_time = models.DateTimeField(verbose_name=_("End Time"))
    character_name = models.CharField(max_length=100, blank=True, verbose_name=_("Character Name"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"))

    @property
    def is_active(self):
        from django.utils import timezone
        return self.end_time > timezone.now() and self.status == 'pending'

    def __str__(self):
        return f"Auction of {self.item_name} ({self.quantity}x) by {self.seller.username}"

    class Meta:
        verbose_name = _("Auction")
        verbose_name_plural = _("Auctions")


class Bid(BaseModel):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE, related_name='bids', verbose_name=_("Auction"))
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Bidder"))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    character_name = models.CharField(max_length=100, blank=True, verbose_name=_("Character Name"))

    def __str__(self):
        return f"{self.bidder.username} bid {self.amount} on {self.auction.item_name}"

    class Meta:
        verbose_name = _("Bid")
        verbose_name_plural = _("Bids")
