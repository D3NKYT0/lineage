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
from utils.notifications import send_notification


logger = logging.getLogger(__name__)


def validar_assinatura_hmac(request):
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    if not x_signature or not x_request_id:
        logger.warning("Cabeçalhos obrigatórios ausentes: x-signature ou x-request-id.")
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
        parts = dict(part.strip().split("=", 1) for part in x_signature.split(","))
        ts = parts.get("ts")
        v1 = parts.get("v1")
    except Exception as e:
        logger.warning(f"Erro ao analisar x-signature: {e}")
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
        return False

    return True


def pagamento_sucesso(request):
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
            return redirect("payment:pagamento_erro")

        pagamento_info = result["response"]
        status_pagamento = pagamento_info["status"]
        pagamento_id = pagamento_info.get("metadata", {}).get("pagamento_id")

        if not pagamento_id:
            logger.warning("Pagamento sem metadata.pagamento_id.")
            return redirect("payment:pagamento_erro")

        pagamento = Pagamento.objects.get(id=pagamento_id)

        # garantia do pagamento
        if status_pagamento == "approved" and pagamento.status != "paid" and pagamento.status == "approved":
            with transaction.atomic():
                wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                aplicar_transacao(
                    wallet=wallet,
                    tipo="ENTRADA",
                    valor=pagamento.valor,
                    descricao="Crédito via MercadoPago (fallback)",
                    origem="MercadoPago",
                    destino=pagamento.usuario.username
                )
                pagamento.status = "paid"
                pagamento.save()

                pedido = pagamento.pedido_pagamento
                pedido.status = 'CONCLUÍDO'
                pedido.save()

                # REGISTRO DO FALBACK NO WEBHOOKLOG
                WebhookLog.objects.create(
                    tipo="payment_fallback",
                    data_id=str(payment_id),
                    payload=pagamento_info
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


@csrf_exempt
@require_POST
def notificacao_mercado_pago(request):
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
                        if status == "approved" and pagamento.status == "pending":
                            with transaction.atomic():
                                # Usa o novo sistema de bônus
                                from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                                from decimal import Decimal
                                
                                wallet, created = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                                valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                                    wallet, Decimal(str(pagamento.valor)), "MercadoPago"
                                )
                                
                                pagamento.status = "paid"
                                pagamento.save()

                                pedido = pagamento.pedido_pagamento
                                pedido.bonus_aplicado = valor_bonus
                                pedido.total_creditado = valor_total
                                pedido.status = 'CONCLUÍDO'
                                pedido.save()

                                try:
                                    # Notificação para staff
                                    send_notification(
                                        user=None,
                                        notification_type='staff',
                                        message=f"Pagamento aprovado para {pagamento.usuario.username} no valor de R$ {pagamento.valor:.2f}.",
                                        created_by=pagamento.usuario
                                    )
                                except Exception as e:
                                    logger.error(f"Erro ao criar notificação: {str(e)}")

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
                            if pagamento.status == "pending":
                                pagamento.status = "approved"
                                pagamento.save()
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
