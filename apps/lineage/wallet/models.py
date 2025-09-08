from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from core.models import BaseModel
from decimal import Decimal


class Wallet(BaseModel):
    usuario = models.OneToOneField(User, verbose_name=_("Usuário"), on_delete=models.CASCADE)
    saldo = models.DecimalField(_("Saldo"), max_digits=10, decimal_places=2, default=0.00)
    saldo_bonus = models.DecimalField(_("Saldo Bônus"), max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        verbose_name = _("Carteira")
        verbose_name_plural = _("Carteiras")

    def __str__(self):
        return f"Carteira de {self.usuario.username} - Saldo: R${self.saldo} | Bônus: R${self.saldo_bonus}"


class TransacaoWallet(BaseModel):
    TIPO = [
        ('ENTRADA', _("Entrada")),
        ('SAIDA', _("Saída")),
    ]

    wallet = models.ForeignKey(Wallet, verbose_name=_("Carteira"), on_delete=models.CASCADE, related_name='transacoes')
    tipo = models.CharField(_("Tipo"), max_length=10, choices=TIPO)
    valor = models.DecimalField(_("Valor"), max_digits=10, decimal_places=2)
    descricao = models.TextField(_("Descrição"), blank=True)
    data = models.DateTimeField(_("Data da Transação"), auto_now_add=True)
    origem = models.CharField(_("Origem"), max_length=100, blank=True)  # Ex: "Pix", "Venda"
    destino = models.CharField(_("Destino"), max_length=100, blank=True) # Ex: "Fulano", "MercadoPago"

    class Meta:
        verbose_name = _("Transação da Carteira")
        verbose_name_plural = _("Transações da Carteira")

    def __str__(self):
        return f"{self.tipo} de R${self.valor} - {self.data.strftime('%d/%m/%Y %H:%M')}"


class TransacaoBonus(BaseModel):
    TIPO = [
        ('ENTRADA', _("Entrada")),
        ('SAIDA', _("Saída")),
    ]

    wallet = models.ForeignKey(Wallet, verbose_name=_("Carteira"), on_delete=models.CASCADE, related_name='transacoes_bonus')
    tipo = models.CharField(_("Tipo"), max_length=10, choices=TIPO)
    valor = models.DecimalField(_("Valor"), max_digits=10, decimal_places=2)
    descricao = models.TextField(_("Descrição"), blank=True)
    data = models.DateTimeField(_("Data da Transação"), auto_now_add=True)
    origem = models.CharField(_("Origem"), max_length=100, blank=True)
    destino = models.CharField(_("Destino"), max_length=100, blank=True)

    class Meta:
        verbose_name = _("Transação de Bônus")
        verbose_name_plural = _("Transações de Bônus")

    def __str__(self):
        return f"BÔNUS {self.tipo} de R${self.valor} - {self.data.strftime('%d/%m/%Y %H:%M')}"


class CoinConfig(BaseModel):
    nome = models.CharField(_("Nome da Moeda"), max_length=100)
    coin_id = models.PositiveIntegerField(_("ID da Moeda"), default=57)
    multiplicador = models.DecimalField(
        _("Multiplicador (ex: 2.0 para 2x)"), max_digits=5, decimal_places=2, default=1.0
    )
    ativa = models.BooleanField(_("Moeda Ativa"), default=True)

    class Meta:
        verbose_name = _("Configuração de Moeda")
        verbose_name_plural = _("Configurações de Moeda")

    def save(self, *args, **kwargs):
        # Se esta moeda está sendo ativada, desativa todas as outras
        if self.ativa:
            # Usa update() para evitar recursão infinita
            CoinConfig.objects.exclude(pk=self.pk).update(ativa=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - ID: {self.coin_id} - x{self.multiplicador}"


class CoinPurchaseBonus(BaseModel):
    valor_minimo = models.DecimalField(
        _("Valor Mínimo (R$)"), 
        max_digits=10, 
        decimal_places=2,
        help_text=_("Valor mínimo da compra para aplicar o bônus")
    )
    valor_maximo = models.DecimalField(
        _("Valor Máximo (R$)"), 
        max_digits=10, 
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Valor máximo da compra (deixe em branco para sem limite)")
    )
    bonus_percentual = models.DecimalField(
        _("Bônus (%)"), 
        max_digits=5, 
        decimal_places=2,
        help_text=_("Percentual de bônus a ser aplicado (ex: 10.00 para 10%)")
    )
    descricao = models.CharField(
        _("Descrição"), 
        max_length=200,
        help_text=_("Descrição do bônus (ex: 'Bônus de 10% para compras acima de R$ 50')")
    )
    ativo = models.BooleanField(_("Ativo"), default=True)
    ordem = models.PositiveIntegerField(
        _("Ordem"), 
        default=0,
        help_text=_("Ordem de prioridade (menor número = maior prioridade)")
    )

    class Meta:
        verbose_name = _("Bônus de Compra de Moedas")
        verbose_name_plural = _("Bônus de Compra de Moedas")
        ordering = ['ordem', 'valor_minimo']

    def __str__(self):
        if self.valor_maximo:
            return f"{self.descricao} ({self.valor_minimo} - {self.valor_maximo})"
        else:
            return f"{self.descricao} (≥ {self.valor_minimo})"

    def calcular_bonus(self, valor_compra):
        """Calcula o valor do bônus baseado no valor da compra"""
        # Garante que valor_compra seja Decimal
        valor_compra = Decimal(str(valor_compra))
        
        if valor_compra < self.valor_minimo:
            return Decimal('0.00')
        
        if self.valor_maximo and valor_compra > self.valor_maximo:
            return Decimal('0.00')
            
        return (valor_compra * self.bonus_percentual) / Decimal('100.00')

    @classmethod
    def obter_bonus_para_valor(cls, valor_compra):
        """Retorna o bônus aplicável para um determinado valor de compra"""
        bonus = cls.objects.filter(
            ativo=True,
            valor_minimo__lte=valor_compra
        ).exclude(
            valor_maximo__lt=valor_compra
        ).order_by('ordem', 'valor_minimo').first()
        
        return bonus
