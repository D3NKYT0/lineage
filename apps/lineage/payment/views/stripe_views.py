import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.wallet.models import Wallet
from utils.notifications import send_notification
from ..models import Pagamento, WebhookLog
import logging
from django.shortcuts import render, redirect


logger = logging.getLogger(__name__)


stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.warning("Payload inválido.")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning("Assinatura inválida.")
        return HttpResponse(status=400)

    logger.info(f"Evento Stripe recebido: {event['type']}")

    WebhookLog.objects.create(
        tipo=event["type"],
        data_id=event["id"],
        payload=event
    )

    # Tratamento de evento
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        pagamento_id = session.get('metadata', {}).get('pagamento_id')
        valor = float(session['amount_total']) / 100  # Stripe envia em centavos

        if pagamento_id:
            try:
                pagamento = Pagamento.objects.get(id=pagamento_id)
                if pagamento.status == "pending":
                    # Usa o novo sistema de bônus
                    from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                    from decimal import Decimal
                    
                    wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                    valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                        wallet, Decimal(str(valor)), "Stripe"
                    )
                    
                    pagamento.status = "paid"
                    pagamento.save()

                    pedido = pagamento.pedido_pagamento
                    pedido.bonus_aplicado = valor_bonus
                    pedido.total_creditado = valor_total
                    pedido.status = "CONCLUÍDO"
                    pedido.save()

                    send_notification(
                        user=None,
                        notification_type='staff',
                        message=f"Pagamento aprovado para {pagamento.usuario.username} no valor de R$ {valor:.2f}.",
                        created_by=pagamento.usuario
                    )
            except Pagamento.DoesNotExist:
                logger.error(f"Pagamento ID {pagamento_id} não encontrado.")
                return HttpResponse(status=404)

    return HttpResponse(status=200)


def stripe_pagamento_sucesso(request):
    session_id = request.GET.get("session_id")
    if not session_id:
        return redirect("payment:stripe_pagamento_erro")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        pagamento_id = session.get("metadata", {}).get("pagamento_id")

        if not pagamento_id:
            logger.warning("Checkout session sem metadata.pagamento_id.")
            return redirect("payment:stripe_pagamento_erro")

        pagamento = Pagamento.objects.get(id=pagamento_id)

        if session.payment_status == "paid" and pagamento.status != "paid":
            # Usa o novo sistema de bônus
            from apps.lineage.wallet.utils import aplicar_compra_com_bonus
            from decimal import Decimal
            
            wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
            valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                wallet, Decimal(str(pagamento.valor)), "Stripe"
            )
            
            pagamento.status = "paid"
            pagamento.save()

            pedido = pagamento.pedido_pagamento
            pedido.bonus_aplicado = valor_bonus
            pedido.total_creditado = valor_total
            pedido.status = 'CONCLUÍDO'
            pedido.save()

            WebhookLog.objects.create(
                tipo="payment_fallback",
                data_id=session_id,
                payload=session
            )

        return render(request, "stripe/pagamento_sucesso.html")

    except Exception as e:
        logger.exception("Erro ao processar sucesso do Stripe.")
        return redirect("payment:stripe_pagamento_erro")


def stripe_pagamento_erro(request):
    return render(request, "stripe/pagamento_erro.html")
