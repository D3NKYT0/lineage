from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.main.home.models import User
from apps.lineage.wallet.models import Wallet, TransacaoWallet, CoinPurchaseBonus
from core.models import BaseModel
from .choices import *


class PedidoPagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    valor_pago = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount Paid"))
    moedas_geradas = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Coins Generated"))
    bonus_aplicado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Applied Bonus"))
    total_creditado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_("Total Credited"))
    metodo = models.CharField(max_length=100, verbose_name=_("Payment Method"))
    status = models.CharField(max_length=20, default='PENDENTE', verbose_name=_("Status"))  # CONFIRMADO, FALHOU...
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    def confirmar_pagamento(self, actor=None):
        if self.status != 'CONFIRMADO':
            self.status = 'CONFIRMADO'
            self.save()

            wallet, wallet_created = Wallet.objects.get_or_create(usuario=self.usuario)

            # Usa a função centralizada que mantém consistência
            from apps.lineage.wallet.utils import aplicar_compra_com_bonus
            descricao_extra = None
            if actor is not None:
                try:
                    username = getattr(actor, 'username', None) or str(actor)
                except Exception:
                    username = 'admin'
                descricao_extra = f"(confirmação manual por admin: {username})"

            valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                wallet, self.valor_pago, self.metodo, descricao_extra=descricao_extra
            )
            
            # Atualiza os campos de bônus
            self.bonus_aplicado = valor_bonus
            self.total_creditado = valor_total
            self.save()

            # Notifica staff (push) sobre doação/compra na carteira
            try:
                from django.urls import reverse
                from utils.push import send_push_to_staff_for_event, EVENT_ADMIN_DOACOES_COMPRAS
                send_push_to_staff_for_event(
                    EVENT_ADMIN_DOACOES_COMPRAS,
                    username=self.usuario.username,
                    valor=str(self.valor_pago),
                    url=reverse('dashboard'),
                    async_send=True,
                )
            except Exception:
                pass

    def __str__(self):
        bonus_info = f" + R${self.bonus_aplicado} bônus" if self.bonus_aplicado > 0 else ""
        return f"Pedido #{self.id} - {self.usuario.username} - R${self.valor_pago}{bonus_info} - {self.status}"

    class Meta:
        verbose_name = _("Payment Request")
        verbose_name_plural = _("Payment Requests")


class Pagamento(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    valor = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Value"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending', verbose_name=_("Status"), db_index=True)
    transaction_code = models.CharField(max_length=100, null=True, blank=True, verbose_name=_("Transaction Code"))
    pedido_pagamento = models.OneToOneField(
        PedidoPagamento,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Linked Payment Request")
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    processado_em = models.DateTimeField(null=True, blank=True, verbose_name=_("Processed At"))

    def __str__(self):
        return f"Pagamento {self.id} - {self.status}"

    class Meta:
        verbose_name = _("Payment")
        verbose_name_plural = _("Payments")


class WebhookLog(BaseModel):
    tipo = models.CharField(max_length=100, verbose_name=_("Type"))
    data_id = models.CharField(max_length=100, verbose_name=_("Data ID"))
    payload = models.JSONField(verbose_name=_("Payload"))
    recebido_em = models.DateTimeField(auto_now_add=True, verbose_name=_("Received At"))

    class Meta:
        verbose_name = _("Webhook Log")
        verbose_name_plural = _("Webhook Logs")
        indexes = [
            models.Index(fields=['tipo', 'data_id']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.data_id}"


class TentativaFalsificacao(BaseModel):
    """Modelo para rastrear tentativas de falsificação de pagamentos"""
    ip_address = models.GenericIPAddressField(verbose_name=_("IP Address"), db_index=True)
    provedor = models.CharField(max_length=50, choices=[('Stripe', 'Stripe'), ('MercadoPago', 'Mercado Pago')], verbose_name=_("Provider"))
    tipo_tentativa = models.CharField(
        max_length=50,
        choices=[
            ('sem_assinatura', _('Sem Assinatura')),
            ('assinatura_falsa', _('Assinatura Falsa')),
            ('assinatura_malformada', _('Assinatura Malformada')),
            ('valor_modificado', _('Valor Modificado')),
            ('id_falso', _('ID Falso')),
            ('replay_attack', _('Replay Attack')),
        ],
        verbose_name=_("Attempt Type")
    )
    detalhes = models.TextField(blank=True, null=True, verbose_name=_("Details"))
    user_agent = models.CharField(max_length=500, blank=True, null=True, verbose_name=_("User Agent"))
    alerta_enviado = models.BooleanField(default=False, verbose_name=_("Alert Sent"))
    data_tentativa = models.DateTimeField(auto_now_add=True, verbose_name=_("Attempt Date"), db_index=True)

    class Meta:
        verbose_name = _("Fraud Attempt")
        verbose_name_plural = _("Fraud Attempts")
        indexes = [
            models.Index(fields=['ip_address', 'data_tentativa']),
            models.Index(fields=['provedor', 'data_tentativa']),
            models.Index(fields=['alerta_enviado', 'data_tentativa']),
        ]
        ordering = ['-data_tentativa']

    def __str__(self):
        return f"{self.provedor} - {self.tipo_tentativa} - {self.ip_address} - {self.data_tentativa}"

    @classmethod
    def contar_tentativas_recentes(cls, ip_address, minutos=60):
        """Conta tentativas do mesmo IP nos últimos N minutos"""
        from django.utils import timezone
        from datetime import timedelta
        cutoff = timezone.now() - timedelta(minutes=minutos)
        return cls.objects.filter(ip_address=str(ip_address), data_tentativa__gte=cutoff).count()

    @classmethod
    def deve_enviar_alerta(cls, ip_address, limite=5, minutos=60):
        """Verifica se deve enviar alerta baseado no número de tentativas"""
        from django.utils import timezone
        from datetime import timedelta
        
        tentativas = cls.contar_tentativas_recentes(ip_address, minutos)
        # Verifica se já foi enviado alerta recente
        ja_alertado = cls.objects.filter(
            ip_address=str(ip_address),
            alerta_enviado=True,
            data_tentativa__gte=timezone.now() - timedelta(hours=24)
        ).exists()
        return tentativas >= limite and not ja_alertado