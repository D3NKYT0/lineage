from datetime import timedelta
from django.utils.timezone import now
from .models import *
from django.db import transaction
from apps.lineage.wallet.signals import aplicar_transacao


def expirar_pedidos_antigos():
    limite = now() - timedelta(hours=48)
    PedidoPagamento.objects.filter(status='PENDENTE', data_criacao__lt=limite).update(status='EXPIRADO')


def processar_pedidos_aprovados():
    pagamentos = Pagamento.objects.filter(status='approved', pedido_pagamento__status='PENDENTE')
    for pagamento in pagamentos:
        try:
            with transaction.atomic():
                wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                aplicar_transacao(
                    wallet=wallet,
                    tipo="ENTRADA",
                    valor=pagamento.valor,
                    descricao="Crédito via MercadoPago (celery beats)",
                    origem="MercadoPago",
                    destino=pagamento.usuario.username
                )
                pagamento.status = "paid"
                pagamento.save()

                pedido = pagamento.pedido_pagamento
                pedido.status = 'CONCLUÍDO'
                pedido.save()
        except Exception as e:
            # Logar ou tratar o erro de alguma forma
            print(f"Erro ao creditar pagamento {pagamento.id}: {e}")
