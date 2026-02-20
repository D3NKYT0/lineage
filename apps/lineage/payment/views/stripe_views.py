import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.wallet.models import Wallet
from utils.notifications import send_notification
from django.shortcuts import render, redirect
from django.utils import timezone

from core.log_utils import log_action
from ..models import Pagamento, WebhookLog

import logging

logger = logging.getLogger(__name__)


# Configura a chave do Stripe apenas se estiver configurada
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


def validar_stripe():
    """
    Valida se o Stripe está configurado e ativado.
    Retorna (is_valid, error_message)
    """
    if not getattr(settings, 'STRIPE_ACTIVATE_PAYMENTS', False):
        return False, "O método de pagamento Stripe está desativado no momento."
    
    if not getattr(settings, 'STRIPE_SECRET_KEY', None):
        return False, "O Stripe não está configurado corretamente. Entre em contato com o suporte."
    
    return True, None


@csrf_exempt
def stripe_webhook(request):
    # Valida se Stripe está configurado antes de processar webhook
    is_valid, error_msg = validar_stripe()
    if not is_valid:
        logger.error(f"Webhook do Stripe recebido mas Stripe não está configurado: {error_msg}")
        return HttpResponse(status=503)  # Service Unavailable
    
    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.warning("Payload inválido.")
        # Registra tentativa de falsificação
        from ..utils import registrar_tentativa_falsificacao
        registrar_tentativa_falsificacao(
            request, 'Stripe', 'sem_assinatura',
            detalhes=f"Payload inválido: {str(e)}"
        )
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.warning("Assinatura inválida.")
        # Registra tentativa de falsificação
        from ..utils import registrar_tentativa_falsificacao
        registrar_tentativa_falsificacao(
            request, 'Stripe', 'assinatura_falsa',
            detalhes=f"Assinatura inválida: {str(e)}"
        )
        return HttpResponse(status=400)

    logger.info(f"Evento Stripe recebido: {event['type']}")

    if not WebhookLog.objects.filter(tipo=event["type"], data_id=str(event["id"])):
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
                    pagamento.processado_em = timezone.now()
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
                        created_by=None
                    )
                    log_action(
                        logger, "payment_stripe_webhook", "checkout_completed",
                        username=pagamento.usuario.username,
                        pagamento_id=pagamento_id,
                        valor=str(valor),
                        valor_bonus=str(valor_bonus),
                    )
            except Pagamento.DoesNotExist:
                logger.error(f"Pagamento ID {pagamento_id} não encontrado.")
                return HttpResponse(status=404)

    elif event['type'] == 'payment_intent.succeeded':
        # Fallback: caso o Checkout não dispare/chegue a tempo
        intent = event['data']['object']
        meta = intent.get('metadata', {}) or {}
        pagamento_id = meta.get('pagamento_id')
        if pagamento_id:
            try:
                pagamento = Pagamento.objects.get(id=pagamento_id)
                if pagamento.status == "pending":
                    from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                    from decimal import Decimal
                    wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                    valor_total, valor_bonus, _ = aplicar_compra_com_bonus(
                        wallet, Decimal(str(pagamento.valor)), "Stripe"
                    )
                    pagamento.status = "paid"
                    pagamento.processado_em = timezone.now()
                    pagamento.save()
                    pedido = pagamento.pedido_pagamento
                    if pedido:
                        pedido.bonus_aplicado = valor_bonus
                        pedido.total_creditado = valor_total
                        pedido.status = "CONCLUÍDO"
                        pedido.save()
                    log_action(
                        logger, "payment_stripe_webhook", "payment_intent_succeeded",
                        username=pagamento.usuario.username,
                        pagamento_id=pagamento_id,
                        valor=str(pagamento.valor),
                        valor_bonus=str(valor_bonus),
                    )
            except Pagamento.DoesNotExist:
                logger.error(f"Pagamento ID {pagamento_id} (PI) não encontrado.")

    return HttpResponse(status=200)


def stripe_pagamento_sucesso(request):
    # Valida se Stripe está configurado e ativado
    is_valid, error_msg = validar_stripe()
    if not is_valid:
        logger.error(f"Tentativa de acessar sucesso do Stripe mas Stripe não está configurado: {error_msg}")
        from django.contrib import messages
        messages.error(request, error_msg)
        return redirect("payment:stripe_pagamento_erro")
    
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
            log_action(
                logger, "payment_stripe", "aprovado_redirect",
                username=pagamento.usuario.username,
                pagamento_id=pagamento_id,
                session_id=session_id,
                valor=str(pagamento.valor),
                valor_bonus=str(valor_bonus),
            )

        return render(request, "stripe/pagamento_sucesso.html")

    except stripe.error.AuthenticationError as e:
        # Erro de autenticação - API key inválida ou não configurada
        logger.error(f"Erro de autenticação do Stripe: {str(e)}. Verifique se CONFIG_STRIPE_SECRET_KEY está configurado corretamente.")
        from django.contrib import messages
        messages.error(request, "Erro de configuração do sistema de pagamento. Por favor, entre em contato com o suporte.")
        return redirect("payment:stripe_pagamento_erro")
    except stripe.error.InvalidRequestError as e:
        # Session ID inválido - possível tentativa de falsificação
        logger.warning(f"Session ID inválido: {session_id}")
        from ..utils import registrar_tentativa_falsificacao
        registrar_tentativa_falsificacao(
            request, 'Stripe', 'id_falso',
            detalhes=f"Session ID inválido: {session_id} - {str(e)}"
        )
        return redirect("payment:stripe_pagamento_erro")
    except Exception as e:
        logger.exception("Erro ao processar sucesso do Stripe.")
        from django.contrib import messages
        messages.error(request, "Erro ao processar pagamento. Por favor, tente novamente.")
        return redirect("payment:stripe_pagamento_erro")


def stripe_pagamento_erro(request):
    return render(request, "stripe/pagamento_erro.html")
