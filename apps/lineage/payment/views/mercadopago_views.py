from django.shortcuts import render, redirect
from django.conf import settings
import mercadopago
from ..models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.wallet.models import Wallet
from django.db import transaction
import logging
import hmac
import hashlib
import urllib.parse
from django.utils import timezone

from core.log_utils import log_action
from utils.notifications import send_notification

logger = logging.getLogger(__name__)


def validar_mercado_pago():
    """
    Valida se o Mercado Pago está configurado e ativado.
    Retorna (is_valid, error_message)
    """
    if not getattr(settings, 'MERCADO_PAGO_ACTIVATE_PAYMENTS', False):
        return False, "O método de pagamento Mercado Pago está desativado no momento."
    
    if not getattr(settings, 'MERCADO_PAGO_ACCESS_TOKEN', None):
        return False, "O Mercado Pago não está configurado corretamente. Entre em contato com o suporte."
    
    return True, None


def validar_assinatura_hmac(request):
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    if not x_signature or not x_request_id:
        logger.warning("Cabeçalhos obrigatórios ausentes: x-signature ou x-request-id.")
        # Registra tentativa de falsificação
        from ..utils import registrar_tentativa_falsificacao
        registrar_tentativa_falsificacao(
            request, 'MercadoPago', 'sem_assinatura',
            detalhes="Cabeçalhos obrigatórios ausentes"
        )
        return False

    # Pega o data.id da query string ou do corpo da requisição
    query_string = urllib.parse.urlparse(request.build_absolute_uri()).query
    query_params = urllib.parse.parse_qs(query_string)
    data_id = query_params.get("data.id", [None])[0]

    # Se não veio pela query string, tenta pegar do corpo
    if not data_id:
        try:
            body_data = json.loads(request.body)
            data_id = body_data.get("data", {}).get("id") or body_data.get("id")
        except Exception as e:
            logger.warning(f"Falha ao extrair data.id do corpo da requisição: {e}")
            return False

    if not data_id:
        logger.warning("Parâmetro 'data.id' ausente na query string e no corpo.")
        return False

    # Extrai ts e v1 da assinatura
    try:
        parts = {}
        for part in x_signature.split(","):
            part = part.strip()
            if not part:
                continue
            # Verifica se a parte tem o formato correto (chave=valor)
            if "=" not in part:
                logger.warning(f"Formato inválido na parte da assinatura: {part}")
                # Registra tentativa de falsificação
                from ..utils import registrar_tentativa_falsificacao
                registrar_tentativa_falsificacao(
                    request, 'MercadoPago', 'assinatura_malformada',
                    detalhes=f"Formato inválido: {part}"
                )
                return False
            key, value = part.split("=", 1)
            parts[key.strip()] = value.strip()
        ts = parts.get("ts")
        v1 = parts.get("v1")
    except (ValueError, AttributeError) as e:
        logger.warning(f"Erro ao analisar x-signature: {e}")
        # Registra tentativa de falsificação
        from ..utils import registrar_tentativa_falsificacao
        registrar_tentativa_falsificacao(
            request, 'MercadoPago', 'assinatura_malformada',
            detalhes=f"Erro ao analisar: {str(e)}"
        )
        return False

    if not ts or not v1:
        logger.warning("Partes 'ts' ou 'v1' da assinatura ausentes.")
        return False

    # Monta o manifest de acordo com a documentação oficial
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

    try:
        secret = settings.MERCADO_PAGO_WEBHOOK_SECRET
    except AttributeError:
        logger.error("Chave secreta do Mercado Pago não configurada no settings.")
        return False

    hmac_obj = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256)
    expected_signature = hmac_obj.hexdigest()

    if not hmac.compare_digest(expected_signature, v1):
        logger.warning("Assinatura HMAC inválida.")
        # Registra tentativa de falsificação
        from ..utils import registrar_tentativa_falsificacao
        registrar_tentativa_falsificacao(
            request, 'MercadoPago', 'assinatura_falsa',
            detalhes="HMAC inválido"
        )
        return False

    return True


def pagamento_sucesso(request):
    # Valida se Mercado Pago está configurado e ativado
    is_valid, error_msg = validar_mercado_pago()
    if not is_valid:
        logger.error(f"Tentativa de acessar sucesso do Mercado Pago mas não está configurado: {error_msg}")
        from django.contrib import messages
        messages.error(request, error_msg)
        return redirect("payment:pagamento_erro")
    
    payment_id = request.GET.get("payment_id")
    status = request.GET.get("status")

    if not payment_id or status != "approved":
        logger.warning("Pagamento não aprovado ou parâmetros inválidos na URL de sucesso.")
        return redirect("payment:pagamento_erro")  # Redireciona para view de erro

    try:
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        result = sdk.payment().get(payment_id)

        if result["status"] != 200:
            logger.error("Erro ao consultar o pagamento no Mercado Pago.")
            # Registra tentativa de falsificação (payment_id inválido)
            from ..utils import registrar_tentativa_falsificacao
            registrar_tentativa_falsificacao(
                request, 'MercadoPago', 'id_falso',
                detalhes=f"Payment ID inválido: {payment_id} - Status: {result.get('status')}"
            )
            return redirect("payment:pagamento_erro")

        pagamento_info = result["response"]
        status_pagamento = pagamento_info["status"]
        pagamento_id = pagamento_info.get("metadata", {}).get("pagamento_id")

        if not pagamento_id:
            logger.warning("Pagamento sem metadata.pagamento_id.")
            return redirect("payment:pagamento_erro")

        pagamento = Pagamento.objects.get(id=pagamento_id)

        # Idempotência e consistência com o webhook
        if status_pagamento == "approved":
            pedido = pagamento.pedido_pagamento
            pedido_ja_processado = False
            if pedido:
                pedido_ja_processado = pedido.status in ("CONFIRMADO", "CONCLUÍDO")

            if pagamento.status in ("pending", "approved") and not pedido_ja_processado:
                with transaction.atomic():
                    # Usa o mesmo caminho de crédito do webhook
                    from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                    from decimal import Decimal

                    wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                    valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                        wallet, Decimal(str(pagamento.valor)), "MercadoPago"
                    )

                    pagamento.status = "paid"
                    pagamento.processado_em = timezone.now()
                    pagamento.save()

                    if pedido:
                        pedido.bonus_aplicado = valor_bonus
                        pedido.total_creditado = valor_total
                        pedido.status = 'CONCLUÍDO'
                        pedido.save()

                    if not WebhookLog.objects.filter(tipo="payment_fallback", data_id=str(payment_id)).exists():
                        WebhookLog.objects.create(
                            tipo="payment_fallback",
                            data_id=str(payment_id),
                            payload=pagamento_info
                        )
                    log_action(
                        logger, "payment_mercadopago", "aprovado_redirect",
                        username=pagamento.usuario.username,
                        pagamento_id=pagamento_id,
                        payment_id_mp=payment_id,
                        valor=str(pagamento.valor),
                        valor_bonus=str(valor_bonus),
                    )

        return render(request, 'mp/pagamento_sucesso.html')

    except Pagamento.DoesNotExist:
        logger.error(f"Pagamento com ID {pagamento_id} não encontrado.")
        return redirect("payment:pagamento_erro")

    except Exception as e:
        logger.exception(f"Erro inesperado na view pagamento_sucesso: {e}")
        return redirect("payment:pagamento_erro")


def pagamento_erro(request):
    return render(request, 'mp/pagamento_erro.html')


def pagamento_pendente(request):
    return render(request, 'mp/pagamento_pendente.html')


@csrf_exempt
@require_POST
def notificacao_mercado_pago(request):
    # Valida se Mercado Pago está configurado antes de processar webhook
    is_valid, error_msg = validar_mercado_pago()
    if not is_valid:
        logger.error(f"Webhook do Mercado Pago recebido mas não está configurado: {error_msg}")
        return HttpResponse(status=503)  # Service Unavailable
    
    # A validação já registra tentativas de falsificação internamente
    if not validar_assinatura_hmac(request):
        return HttpResponse("Assinatura inválida", status=400)

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return HttpResponse("JSON inválido", status=400)

    tipo = body.get("type")
    data = body.get("data", {})

    if not tipo:
        return HttpResponse("Parâmetros inválidos", status=400)

    # Trata notificações alternativas como equivalentes
    if tipo == "topic_merchant_order_wh":
        tipo = "merchant_order"

    # Identifica o ID da entidade conforme o tipo
    if tipo in ["payment", "plan", "subscription", "invoice"]:
        data_id = data.get("id")
    elif tipo == "merchant_order":
        data_id = body.get("id")  # merchant_order manda direto no root
    else:
        data_id = body.get("id")

    if not data_id:
        return HttpResponse("ID não encontrado", status=400)

    logger.info(f"Webhook recebido | Tipo: {tipo} | ID: {data_id}")

    # Evita log duplicado do mesmo evento
    if not WebhookLog.objects.filter(tipo=tipo, data_id=str(data_id)).exists():
        WebhookLog.objects.create(
            tipo=tipo,
            data_id=str(data_id),
            payload=body
        )

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    try:
        if tipo == "payment":
            result = sdk.payment().get(data_id)
            if result["status"] == 200:
                pagamento_info = result["response"]
                status = pagamento_info["status"]
                pagamento_id = pagamento_info.get("metadata", {}).get("pagamento_id")

                if pagamento_id:
                    try:
                        pagamento = Pagamento.objects.get(id=pagamento_id)
                        # Idempotência: só processa se ainda estiver pendente e o pedido não tiver sido confirmado/concluído manualmente
                        pedido = pagamento.pedido_pagamento
                        pedido_ja_processado = False
                        if pedido:
                            pedido_ja_processado = pedido.status in ("CONFIRMADO", "CONCLUÍDO")

                        if status == "approved" and pagamento.status == "pending" and not pedido_ja_processado:
                            with transaction.atomic():
                                # Usa o novo sistema de bônus
                                from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                                from decimal import Decimal
                                
                                wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                                valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                                    wallet, Decimal(str(pagamento.valor)), "MercadoPago"
                                )
                                
                                pagamento.status = "paid"
                                pagamento.processado_em = timezone.now()
                                pagamento.save()

                                pedido = pagamento.pedido_pagamento
                                if pedido:
                                    pedido.bonus_aplicado = valor_bonus
                                    pedido.total_creditado = valor_total
                                    # Mantém consistência com fluxo manual: marca como CONCLUÍDO
                                    pedido.status = 'CONCLUÍDO'
                                    pedido.save()

                                try:
                                    send_notification(
                                        user=None,
                                        notification_type='staff',
                                        message=f"Pagamento aprovado para {pagamento.usuario.username} no valor de R$ {pagamento.valor:.2f}.",
                                        created_by=None
                                    )
                                except Exception as e:
                                    logger.error(f"Erro ao criar notificação: {str(e)}")
                                log_action(
                                    logger, "payment_mercadopago_webhook", "aprovado",
                                    username=pagamento.usuario.username,
                                    pagamento_id=pagamento_id,
                                    data_id=data_id,
                                    valor=str(pagamento.valor),
                                    valor_bonus=str(valor_bonus),
                                )

                        return HttpResponse("OK", status=200)

                    except Pagamento.DoesNotExist:
                        return HttpResponse("Pagamento não encontrado", status=404)
            return HttpResponse("Erro ao consultar pagamento", status=400)

        elif tipo == "merchant_order":
            result = sdk.merchant_order().get(data_id)
            if result["status"] == 200:
                order = result["response"]
                pagamentos = order.get("payments", [])
                aprovado = any(p.get("status") == "approved" for p in pagamentos)

                if aprovado:
                    external_reference = order.get("external_reference")
                    if external_reference:
                        try:
                            pagamento = Pagamento.objects.get(id=external_reference)
                            # Idempotência e consistência: se ainda não processado/concluído, aplica crédito aqui
                            pedido = pagamento.pedido_pagamento
                            pedido_ja_processado = False
                            if pedido:
                                pedido_ja_processado = pedido.status in ("CONFIRMADO", "CONCLUÍDO")

                            if pagamento.status in ("pending", "approved") and not pedido_ja_processado:
                                from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                                from decimal import Decimal
                                with transaction.atomic():
                                    wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                                    valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                                        wallet, Decimal(str(pagamento.valor)), "MercadoPago"
                                    )
                                    pagamento.status = "paid"
                                    pagamento.processado_em = timezone.now()
                                    pagamento.save()

                                    if pedido:
                                        pedido.bonus_aplicado = valor_bonus
                                        pedido.total_creditado = valor_total
                                        pedido.status = 'CONCLUÍDO'
                                        pedido.save()

                                    try:
                                        send_notification(
                                            user=None,
                                            notification_type='staff',
                                            message=f"Pagamento aprovado para {pagamento.usuario.username} no valor de R$ {pagamento.valor:.2f}.",
                                            created_by=None
                                        )
                                    except Exception as e:
                                        logger.error(f"Erro ao criar notificação: {str(e)}")
                                    log_action(
                                        logger, "payment_mercadopago_webhook", "aprovado_merchant_order",
                                        username=pagamento.usuario.username,
                                        pagamento_id=str(pagamento.id),
                                        data_id=data_id,
                                        valor=str(pagamento.valor),
                                        valor_bonus=str(valor_bonus),
                                    )

                            return HttpResponse("OK", status=200)
                        except Pagamento.DoesNotExist:
                            return HttpResponse("Pagamento não encontrado pela referência", status=404)
                return HttpResponse("Ordem ainda não paga", status=200)
            return HttpResponse("Erro ao buscar merchant order", status=400)

        elif tipo == "plan":
            sdk.preapproval().get(data_id)
            logger.info(f"Notificação de plano {data_id} recebida.")
            return HttpResponse("OK", status=200)

        elif tipo == "subscription":
            sdk.preapproval().get(data_id)
            logger.info(f"Notificação de assinatura {data_id} recebida.")
            return HttpResponse("OK", status=200)

        elif tipo == "invoice":
            sdk.invoice().get(data_id)
            logger.info(f"Notificação de fatura {data_id} recebida.")
            return HttpResponse("OK", status=200)

        elif tipo == "point_integration_wh":
            logger.info(f"Notificação Point Integration recebida: {data_id}")
            return HttpResponse("OK", status=200)

        else:
            logger.warning(f"Tipo de notificação não tratado: {tipo} | data_id: {data_id} | payload: {json.dumps(body)}")
            return HttpResponse("Tipo não suportado", status=200)

    except Exception as e:
        logger.exception(f"Erro ao processar notificação do tipo '{tipo}' com data_id '{data_id}': {e}")
        return HttpResponse("Erro interno", status=500)
