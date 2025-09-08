from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PedidoPagamento


@receiver(post_save, sender=PedidoPagamento)
def processar_pagamento_automatico(sender, instance, created, **kwargs):
    # Só processa se não estiver confirmado ainda
    if instance.status == 'PAGO':
        # Evita reprocessar se já tiver confirmado antes
        if not PedidoPagamento.objects.filter(id=instance.id, status='CONFIRMADO').exists():
            instance.confirmar_pagamento()
