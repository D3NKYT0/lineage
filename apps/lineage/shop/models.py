from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel
from decimal import Decimal


class ShopItem(BaseModel):
    nome = models.CharField(_("Nome"), max_length=100)
    item_id = models.PositiveIntegerField(_("ID do Item"))
    preco = models.DecimalField(_("Preço"), max_digits=10, decimal_places=2)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)
    ativo = models.BooleanField(_("Ativo"), default=True)

    class Meta:
        verbose_name = _("Item da Loja")
        verbose_name_plural = _("Itens da Loja")

    def __str__(self):
        return f"{self.nome} ({self.quantidade}x) — R${self.preco}"


class PromotionCode(BaseModel):
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    desconto_percentual = models.DecimalField(_("Desconto Percentual"), max_digits=5, decimal_places=2)
    ativo = models.BooleanField(_("Ativo"), default=True)
    validade = models.DateTimeField(_("Validade"), null=True, blank=True)
    apoiador = models.ForeignKey(
        'server.Apoiador', verbose_name=_("Apoiador"), null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Código Promocional")
        verbose_name_plural = _("Códigos Promocionais")

    def is_valido(self):
        if not self.ativo:
            return False
        if self.validade and timezone.now() > self.validade:
            return False
        return True

    def __str__(self):
        return f"{self.codigo} — {self.desconto_percentual}%"


class ShopPackage(BaseModel):
    nome = models.CharField(_("Nome"), max_length=100)
    preco_total = models.DecimalField(_("Preço Total"), max_digits=10, decimal_places=2)
    itens = models.ManyToManyField(ShopItem, through='ShopPackageItem', verbose_name=_("Itens"))
    ativo = models.BooleanField(_("Ativo"), default=True)
    promocao = models.ForeignKey(
        PromotionCode, verbose_name=_("Promoção"), null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Pacote da Loja")
        verbose_name_plural = _("Pacotes da Loja")

    def __str__(self):
        return f"{self.nome} — R${self.preco_total}"


class ShopPackageItem(BaseModel):
    pacote = models.ForeignKey(ShopPackage, verbose_name=_("Pacote"), on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, verbose_name=_("Item"), on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)

    class Meta:
        verbose_name = _("Item do Pacote")
        verbose_name_plural = _("Itens do Pacote")

    def __str__(self):
        return f"{self.pacote.nome} — {self.item.nome} x{self.quantidade}"


class Cart(BaseModel):
    user = models.OneToOneField(User, verbose_name=_("Usuário"), on_delete=models.CASCADE, related_name='cart')
    itens = models.ManyToManyField(ShopItem, through='CartItem', verbose_name=_("Itens"))
    pacotes = models.ManyToManyField(ShopPackage, through='CartPackage', verbose_name=_("Pacotes"))
    promocao_aplicada = models.ForeignKey(
        PromotionCode, verbose_name=_("Promoção Aplicada"), null=True, blank=True, on_delete=models.SET_NULL
    )
    # Campos para pagamento com bônus
    usar_bonus = models.BooleanField(_("Usar Bônus"), default=False)
    valor_bonus_usado = models.DecimalField(_("Valor Bônus Usado"), max_digits=10, decimal_places=2, default=0.00)
    valor_dinheiro_usado = models.DecimalField(_("Valor Dinheiro Usado"), max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _("Carrinho")
        verbose_name_plural = _("Carrinhos")

    def calcular_total(self):
        total = sum(ci.item.preco * ci.quantidade for ci in self.cartitem_set.all())
        total += sum(cp.pacote.preco_total * cp.quantidade for cp in self.cartpackage_set.all())
        if self.promocao_aplicada and self.promocao_aplicada.is_valido():
            total *= (1 - (self.promocao_aplicada.desconto_percentual / 100))
        return total

    def calcular_pagamento_misto(self, saldo_bonus_disponivel):
        """
        Calcula como o pagamento será dividido entre bônus e dinheiro
        Retorna: (valor_bonus_usado, valor_dinheiro_usado)
        """
        total = self.calcular_total()
        
        if not self.usar_bonus:
            return Decimal('0.00'), total
        
        # Usa bônus primeiro, depois dinheiro
        valor_bonus_usado = min(total, saldo_bonus_disponivel)
        valor_dinheiro_usado = total - valor_bonus_usado
        
        return valor_bonus_usado, valor_dinheiro_usado

    def limpar(self):
        self.itens.clear()
        self.pacotes.clear()
        self.promocao_aplicada = None
        self.usar_bonus = False
        self.valor_bonus_usado = Decimal('0.00')
        self.valor_dinheiro_usado = Decimal('0.00')
        self.save()

    def __str__(self):
        return f"Carrinho de {self.user.username}"


class CartItem(BaseModel):
    cart = models.ForeignKey(Cart, verbose_name=_("Carrinho"), on_delete=models.CASCADE)
    item = models.ForeignKey(ShopItem, verbose_name=_("Item"), on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)

    class Meta:
        verbose_name = _("Item no Carrinho")
        verbose_name_plural = _("Itens no Carrinho")
        unique_together = ['cart', 'item']  # Garante que não existam duplicatas

    def __str__(self):
        return f"{self.quantidade}x {self.item.nome} (Carrinho de {self.cart.user.username})"


class CartPackage(BaseModel):
    cart = models.ForeignKey(Cart, verbose_name=_("Carrinho"), on_delete=models.CASCADE)
    pacote = models.ForeignKey(ShopPackage, verbose_name=_("Pacote"), on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)

    class Meta:
        verbose_name = _("Pacote no Carrinho")
        verbose_name_plural = _("Pacotes no Carrinho")

    def __str__(self):
        return f"{self.quantidade}x {self.pacote.nome} (Carrinho de {self.cart.user.username})"


class ShopPurchase(BaseModel):
    user = models.ForeignKey(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    character_name = models.CharField(_("Nome do Personagem"), max_length=100)
    total_pago = models.DecimalField(_("Total Pago"), max_digits=10, decimal_places=2)
    # Campos para registrar o tipo de pagamento
    valor_bonus_usado = models.DecimalField(_("Valor Bônus Usado"), max_digits=10, decimal_places=2, default=0.00)
    valor_dinheiro_usado = models.DecimalField(_("Valor Dinheiro Usado"), max_digits=10, decimal_places=2, default=0.00)
    promocao_aplicada = models.ForeignKey(
        PromotionCode, verbose_name=_("Promoção Aplicada"), null=True, blank=True, on_delete=models.SET_NULL
    )
    apoiador = models.ForeignKey(
        'server.Apoiador', verbose_name=_("Apoiador"), null=True, blank=True, on_delete=models.SET_NULL
    )
    data_compra = models.DateTimeField(_("Data da Compra"), auto_now_add=True)

    class Meta:
        verbose_name = _("Compra")
        verbose_name_plural = _("Compras")

    def save(self, *args, **kwargs):
        if self.promocao_aplicada and self.promocao_aplicada.apoiador:
            self.apoiador = self.promocao_aplicada.apoiador
        super().save(*args, **kwargs)

    def __str__(self):
        bonus_info = f" (Bônus: R${self.valor_bonus_usado})" if self.valor_bonus_usado > 0 else ""
        return f"Compra de {self.user.username} — R${self.total_pago}{bonus_info} — {self.data_compra.strftime('%d/%m/%Y %H:%M')}"


class PurchaseItem(BaseModel):
    purchase = models.ForeignKey(ShopPurchase, verbose_name=_("Compra"), on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(_("Nome do Item"), max_length=100)
    item_id = models.PositiveIntegerField(_("ID do Item"))
    quantidade = models.PositiveIntegerField(_("Quantidade"), default=1)
    preco_unitario = models.DecimalField(_("Preço Unitário"), max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(_("Preço Total"), max_digits=10, decimal_places=2)
    tipo_compra = models.CharField(_("Tipo de Compra"), max_length=20, choices=[
        ('item', _('Item Individual')),
        ('pacote', _('Pacote')),
    ], default='item')
    nome_pacote = models.CharField(_("Nome do Pacote"), max_length=100, blank=True, null=True)

    class Meta:
        verbose_name = _("Item da Compra")
        verbose_name_plural = _("Itens da Compra")

    def __str__(self):
        if self.tipo_compra == 'pacote' and self.nome_pacote:
            return f"{self.nome_pacote} — {self.item_name} x{self.quantidade}"
        return f"{self.item_name} x{self.quantidade} — R${self.preco_total}"
