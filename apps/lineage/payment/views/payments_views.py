from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import mercadopago
import stripe
from ..models import *
from django.http import HttpResponse, JsonResponse
from apps.main.home.decorator import conditional_otp_required
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
from django.db import transaction
from apps.main.home.models import PerfilGamer
from apps.lineage.wallet.utils import calcular_bonus_compra
from decimal import Decimal
from django.urls import reverse
import logging

from core.log_utils import log_action

logger = logging.getLogger(__name__)

# Configura a chave do Stripe apenas se estiver configurada
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


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


@conditional_otp_required
def calcular_bonus_ajax(request):
    """View para calcular bônus via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        valor = Decimal(request.POST.get('valor', '0'))
        if valor <= 0:
            return JsonResponse({'error': 'Valor inválido'}, status=400)
        
        valor_bonus, descricao_bonus, percentual_bonus = calcular_bonus_compra(valor)
        total_creditado = valor + valor_bonus
        
        return JsonResponse({
            'success': True,
            'valor_compra': float(valor),
            'valor_bonus': float(valor_bonus),
            'bonus_percentual': float(percentual_bonus),
            'total_creditado': float(total_creditado),
            'descricao_bonus': descricao_bonus or '',
            'tem_bonus': valor_bonus > 0
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@conditional_otp_required
def criar_ou_reaproveitar_pedido(request):
    if request.method == 'POST':
        try:
            valor = Decimal(request.POST.get('valor'))
            if valor <= 0:
                return HttpResponse("Valor inválido", status=400)
        except (TypeError, ValueError):
            return HttpResponse("Valor inválido", status=400)

        metodo = request.POST.get('metodo')
        if metodo not in settings.METHODS_PAYMENTS:  # Expanda conforme necessário
            return HttpResponse("Método de pagamento inválido", status=400)
        
        if metodo == "MercadoPago":
            is_valid, error_msg = validar_mercado_pago()
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('payment:novo_pedido')
        
        if metodo == "Stripe":
            is_valid, error_msg = validar_stripe()
            if not is_valid:
                messages.error(request, error_msg)
                return redirect('payment:novo_pedido')

        usuario = request.user
        duas_horas_atras = now() - timedelta(hours=2)

        with transaction.atomic():
            # Lock em todos os pedidos pendentes parecidos do usuário (para evitar criação duplicada)
            pedidos_similares = (
                PedidoPagamento.objects
                .select_for_update()
                .filter(
                    usuario=usuario,
                    valor_pago=valor,
                    metodo=metodo,
                    status='PENDENTE',
                    data_criacao__gte=duas_horas_atras
                )
            )

            pedido_existente = pedidos_similares.first()
            if pedido_existente:
                return redirect('payment:detalhes_pedido', pedido_id=pedido_existente.id)

            # Calcula o bônus para este valor
            valor_bonus, descricao_bonus, percentual_bonus = calcular_bonus_compra(valor)
            total_creditado = valor + valor_bonus

            novo_pedido = PedidoPagamento.objects.create(
                usuario=usuario,
                valor_pago=valor,
                moedas_geradas=valor,
                bonus_aplicado=valor_bonus,
                total_creditado=total_creditado,
                metodo=metodo,
                status='PENDENTE'
            )
            log_action(
                logger, "payment_pedido", "criado",
                username=usuario.username,
                pedido_id=novo_pedido.id,
                valor=str(valor),
                metodo=metodo,
                total_creditado=str(total_creditado),
            )

            perfil, _ = PerfilGamer.objects.get_or_create(user=request.user)
            perfil.adicionar_xp(40)

            return redirect('payment:detalhes_pedido', pedido_id=novo_pedido.id)

    # Buscar bônus configurados para exibir no template
    from apps.lineage.wallet.models import CoinPurchaseBonus
    bonus_configurados = CoinPurchaseBonus.objects.filter(ativo=True).order_by('ordem', 'valor_minimo')
    
    return render(request, "payment/purchase.html", {
        'bonus_configurados': bonus_configurados,
        'mercadopago_ativo': getattr(settings, 'MERCADO_PAGO_ACTIVATE_PAYMENTS', False),
        'stripe_ativo': getattr(settings, 'STRIPE_ACTIVATE_PAYMENTS', False),
    })


@conditional_otp_required
def confirmar_pagamento(request, pedido_id):
    try:
        with transaction.atomic():
            pedido = PedidoPagamento.objects.select_for_update().get(id=pedido_id, usuario=request.user)

            if pedido.status != 'PENDENTE':
                return HttpResponse("Pedido já processado ou inválido.")

            pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()
            if pagamento:
                if pedido.metodo == "MercadoPago" and pagamento.transaction_code:
                    is_valid, error_msg = validar_mercado_pago()
                    if not is_valid:
                        messages.error(request, error_msg)
                        return redirect('payment:pedidos_pendentes')
                    
                    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                    preference_response = sdk.preference().get(pagamento.transaction_code)

                    if preference_response.get("status") != 200:
                        return HttpResponse("Erro ao recuperar preferência de pagamento", status=500)

                    preference = preference_response.get("response", {})
                    return redirect(preference["init_point"])

                if pedido.metodo == "Stripe" and pagamento.transaction_code:
                    is_valid, error_msg = validar_stripe()
                    if not is_valid:
                        messages.error(request, error_msg)
                        return redirect('payment:pedidos_pendentes')
                    
                    return redirect(f"https://checkout.stripe.com/pay/{pagamento.transaction_code}")

                return HttpResponse("Já existe um pagamento iniciado para este pedido.", status=400)

            pagamento = Pagamento.objects.create(
                usuario=request.user,
                valor=pedido.valor_pago,
                status="pending",
                pedido_pagamento=pedido
            )

            if pedido.metodo == "MercadoPago":
                # Valida se Mercado Pago está configurado e ativado
                is_valid, error_msg = validar_mercado_pago()
                if not is_valid:
                    messages.error(request, error_msg)
                    return redirect('payment:pedidos_pendentes')
                
                access_token = settings.MERCADO_PAGO_ACCESS_TOKEN

                sdk = mercadopago.SDK(access_token)
                pending_url = request.build_absolute_uri(
                    reverse('payment:pagamento_pendente')
                ) + f"?pagamento_id={pagamento.id}&pedido_id={pedido.id}"
                # Constrói URLs de retorno com base no host atual para evitar inconsistências de domínio
                success_url = request.build_absolute_uri(reverse('payment:pagamento_sucesso'))
                failure_url = request.build_absolute_uri(reverse('payment:pagamento_erro'))

                # Mercado Pago pode exigir HTTPS para auto_return funcionar corretamente
                if success_url.startswith("http://"):
                    success_url = "https://" + success_url[len("http://"):]
                if failure_url.startswith("http://"):
                    failure_url = "https://" + failure_url[len("http://"):]
                if pending_url.startswith("http://"):
                    pending_url = "https://" + pending_url[len("http://"):]

                item_title = f"Crédito para carteira virtual - {getattr(settings, 'PROJECT_NAME', 'PDL')}"
                preference_data = {
                    "items": [{
                        "title": item_title,
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(pedido.valor_pago),
                    }],
                    "external_reference": str(pagamento.id),
                    "notification_url": getattr(settings, 'MERCADO_PAGO_NOTIFICATION_URL', request.build_absolute_uri(reverse('payment:notificacao_mercado_pago'))),
                    "back_urls": {
                        "success": success_url,
                        "failure": failure_url,
                        "pending": pending_url,
                    },
                    "auto_return": "approved",
                    "metadata": {"pagamento_id": pagamento.id}
                }

                try:
                    preference_response = sdk.preference().create(preference_data)
                except Exception as e:
                    return HttpResponse(f"Erro ao criar preferência de pagamento: {str(e)}", status=500)

                status_code = preference_response.get("status")
                if status_code != 201:
                    # Extrai mensagem detalhada da API do Mercado Pago, se houver
                    response_body = preference_response.get("response", {}) or {}
                    message = response_body.get('message') or response_body.get('error') or 'Falha desconhecida no Mercado Pago'
                    cause = None
                    if isinstance(response_body, dict):
                        causes = response_body.get('cause') or response_body.get('causes')
                        if isinstance(causes, list) and len(causes) > 0:
                            cause = causes[0].get('description') or causes[0].get('code')
                    detail = f"{message}"
                    if cause:
                        detail += f" - {cause}"
                    return HttpResponse(f"Erro ao criar preferência de pagamento (HTTP {status_code}): {detail}", status=500)

                preference = preference_response.get("response", {})
                pagamento.transaction_code = preference["id"]
                pagamento.save()

                perfil, _ = PerfilGamer.objects.get_or_create(user=request.user)
                perfil.adicionar_xp(100)

                return redirect(preference["init_point"])

            elif pedido.metodo == "Stripe":
                # Valida se Stripe está configurado e ativado
                is_valid, error_msg = validar_stripe()
                if not is_valid:
                    messages.error(request, error_msg)
                    return redirect('payment:pedidos_pendentes')
                
                product_name = f"Crédito para carteira virtual - {getattr(settings, 'PROJECT_NAME', 'PDL')}"

                # Constrói URLs com base no host atual (evita inconsistência de domínio)
                success_url = request.build_absolute_uri(
                    reverse('payment:stripe_pagamento_sucesso')
                ) + '?session_id={CHECKOUT_SESSION_ID}'
                cancel_url = request.build_absolute_uri(
                    reverse('payment:stripe_pagamento_erro')
                )
                if success_url.startswith("http://"):
                    success_url = "https://" + success_url[len("http://"):]
                if cancel_url.startswith("http://"):
                    cancel_url = "https://" + cancel_url[len("http://"):]

                # Idempotência: amarra criação da sessão ao pagamento
                idempotency_key = f"checkout_session_{pagamento.id}"

                try:
                    session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    mode='payment',
                    allow_promotion_codes=True,
                    client_reference_id=str(pagamento.id),
                    customer_email=getattr(request.user, 'email', None) or None,
                    line_items=[{
                        'price_data': {
                            'currency': 'brl',
                            'product_data': {'name': product_name},
                            'unit_amount': int(pedido.valor_pago * 100),
                        },
                        'quantity': 1,
                    }],
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata={"pagamento_id": pagamento.id},
                    payment_intent_data={
                        'metadata': {
                            'pagamento_id': str(pagamento.id),
                            'pedido_id': str(pedido.id),
                            'usuario_id': str(request.user.id),
                        }
                    }
                , idempotency_key=idempotency_key)
                except stripe.error.AuthenticationError as e:
                    logger.error(f"Erro de autenticação do Stripe: {str(e)}")
                    messages.error(request, "Erro de configuração do sistema de pagamento. Por favor, entre em contato com o suporte.")
                    return redirect('payment:pedidos_pendentes')
                except stripe.error.InvalidRequestError as e:
                    logger.error(f"Erro na requisição do Stripe: {str(e)}")
                    messages.error(request, "Erro ao processar pagamento. Por favor, tente novamente.")
                    return redirect('payment:pedidos_pendentes')
                except Exception as e:
                    logger.error(f"Erro inesperado ao criar sessão do Stripe: {str(e)}")
                    messages.error(request, "Erro ao processar pagamento. Por favor, tente novamente.")
                    return redirect('payment:pedidos_pendentes')

                pagamento.transaction_code = session.id
                pagamento.save()

                perfil, _ = PerfilGamer.objects.get_or_create(user=request.user)
                perfil.adicionar_xp(100)

                return redirect(session.url, code=303)

            return HttpResponse("Método de pagamento não suportado", status=400)

    except PedidoPagamento.DoesNotExist:
        return HttpResponse("Pedido não encontrado.", status=404)


@conditional_otp_required
def status_pagamento_ajax(request):
    pagamento_id = request.GET.get('pagamento_id')
    if not pagamento_id:
        return JsonResponse({'success': False, 'error': 'pagamento_id ausente'}, status=400)

    try:
        pagamento = Pagamento.objects.select_related('pedido_pagamento', 'usuario').get(id=pagamento_id)
        if pagamento.usuario_id != request.user.id:
            return JsonResponse({'success': False, 'error': 'Não autorizado'}, status=403)

        pedido = pagamento.pedido_pagamento
        pagamento_status = pagamento.status
        pedido_status = pedido.status if pedido else None

        concluido = (pagamento_status == 'paid') or (pedido_status in ('CONFIRMADO', 'CONCLUÍDO'))

        # Se ainda não concluiu, tenta um pull no Mercado Pago via merchant_order.search por external_reference
        if not concluido and pedido and pedido.metodo == 'MercadoPago':
            try:
                import mercadopago
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                search = sdk.merchant_order().search({
                    'external_reference': str(pagamento.id)
                })
                if search.get('status') == 200:
                    results = (search.get('response') or {}).get('elements', [])
                    # Procura qualquer ordem com pagamento aprovado
                    for order in results:
                        pagamentos_mp = order.get('payments', [])
                        aprovado = any(p.get('status') == 'approved' for p in pagamentos_mp)
                        if aprovado:
                            # Idempotente: replica a mesma lógica do webhook
                            if pagamento.status == 'pending':
                                from django.db import transaction
                                from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                                from decimal import Decimal
                                with transaction.atomic():
                                    wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                                    valor_total, valor_bonus, descricao_bonus = aplicar_compra_com_bonus(
                                        wallet, Decimal(str(pagamento.valor)), 'MercadoPago'
                                    )
                                    from django.utils import timezone
                                    pagamento.status = 'paid'
                                    pagamento.processado_em = timezone.now()
                                    pagamento.save()
                                    if pedido:
                                        pedido.bonus_aplicado = valor_bonus
                                        pedido.total_creditado = valor_total
                                        pedido.status = 'CONCLUÍDO'
                                        pedido.save()
                            # Atualiza flags locais após processamento
                            pagamento_status = 'paid'
                            pedido_status = 'CONCLUÍDO'
                            concluido = True
                            break
            except Exception:
                # Silencia no polling para não quebrar UX
                pass

        return JsonResponse({
            'success': True,
            'pagamento_status': pagamento_status,
            'pedido_status': pedido_status,
            'concluido': concluido
        })
    except Pagamento.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Pagamento não encontrado'}, status=404)


@conditional_otp_required
def detalhes_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoPagamento, id=pedido_id, usuario=request.user)

    if pedido.status != 'PENDENTE':
        return HttpResponse("Pedido já processado ou inválido.")

    if request.method == 'POST':
        return redirect('payment:confirmar_pagamento', pedido_id=pedido.id)

    return render(request, "payment/detalhes_pedido.html", {"pedido": pedido})


@conditional_otp_required
def pedidos_pendentes(request):
    pedidos = list(PedidoPagamento.objects.filter(usuario=request.user, status='PENDENTE').order_by('-data_criacao'))

    # Anota cada pedido com flag de cancelamento com base no status local do pagamento
    pagamentos = {
        p.pedido_pagamento_id: p
        for p in Pagamento.objects.filter(pedido_pagamento__in=pedidos)
    }

    for pedido in pedidos:
        pg = pagamentos.get(pedido.id)
        pedido.cancelavel = not (pg and pg.status in ('approved', 'paid'))

    return render(request, "payment/pedidos_pendentes.html", {"pedidos": pedidos})


@conditional_otp_required
def cancelar_pedido(request, pedido_id):
    if request.method != 'POST':
        return HttpResponse("Método não permitido", status=405)

    pedido = get_object_or_404(PedidoPagamento, id=pedido_id, usuario=request.user)

    if pedido.status != 'PENDENTE':
        return HttpResponse("Este pedido não pode ser cancelado.", status=400)

    # Verifica se existe pagamento vinculado e se já há indícios de aprovação
    pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()

    # Se já marcado como aprovado/pago localmente, não permite cancelar
    if pagamento and pagamento.status in ('approved', 'paid'):
        return HttpResponse("Pedido já pago/ aprovado. Cancelamento não permitido.", status=400)

    # Poll rápido no provedor antes de cancelar, para evitar cancelamento indevido
    try:
        if pagamento and pedido.metodo == 'MercadoPago':
            import mercadopago
            sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
            search = sdk.merchant_order().search({'external_reference': str(pagamento.id)})
            if search.get('status') == 200:
                results = (search.get('response') or {}).get('elements', [])
                for order in results:
                    pagamentos_mp = order.get('payments', [])
                    aprovado = any(p.get('status') == 'approved' for p in pagamentos_mp)
                    if aprovado:
                        # Se aprovado no provedor, processa crédito idempotente e bloqueia cancelamento
                        from apps.lineage.wallet.models import Wallet
                        from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                        from decimal import Decimal
                        with transaction.atomic():
                            wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                            valor_total, valor_bonus, _ = aplicar_compra_com_bonus(
                                wallet, Decimal(str(pagamento.valor)), 'MercadoPago'
                            )
                            from django.utils import timezone as dj_timezone
                            pagamento.status = 'paid'
                            pagamento.processado_em = dj_timezone.now()
                            pagamento.save()
                            pedido.bonus_aplicado = valor_bonus
                            pedido.total_creditado = valor_total
                            pedido.status = 'CONCLUÍDO'
                            pedido.save()
                        return HttpResponse("Pagamento aprovado. Pedido concluído. Cancelamento não permitido.", status=400)

        if pagamento and pedido.metodo == 'Stripe' and pagamento.transaction_code:
            # Consulta a sessão do Stripe para confirmar status
            try:
                is_valid, error_msg = validar_stripe()
                if not is_valid:
                    # Se Stripe não está configurado, não tenta consultar
                    pass
                else:
                    session = stripe.checkout.Session.retrieve(pagamento.transaction_code)
                    # Stripe: payment_status 'paid' ou status 'complete' indicam sucesso
                    if getattr(session, 'payment_status', None) == 'paid' or getattr(session, 'status', None) == 'complete':
                        from apps.lineage.wallet.models import Wallet
                        from apps.lineage.wallet.utils import aplicar_compra_com_bonus
                        from decimal import Decimal
                        with transaction.atomic():
                            wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                            valor_total, valor_bonus, _ = aplicar_compra_com_bonus(
                                wallet, Decimal(str(pagamento.valor)), 'Stripe'
                            )
                            from django.utils import timezone as dj_timezone
                            pagamento.status = 'paid'
                            pagamento.processado_em = dj_timezone.now()
                            pagamento.save()
                            pedido.bonus_aplicado = valor_bonus
                            pedido.total_creditado = valor_total
                            pedido.status = 'CONCLUÍDO'
                            pedido.save()
                        return HttpResponse("Pagamento aprovado. Pedido concluído. Cancelamento não permitido.", status=400)
            except stripe.error.AuthenticationError as e:
                logger.error(f"Erro de autenticação do Stripe ao consultar sessão: {str(e)}")
                # Se não conseguir consultar o Stripe, segue o fluxo padrão
                pass
            except Exception:
                # Se não conseguir consultar o Stripe, segue o fluxo padrão
                pass
    except Exception:
        # Em caso de erro no polling, não bloqueia por erro de consulta – segue regra local
        pass

    # Sem indícios de pagamento: pode cancelar
    pedido.status = 'CANCELADO'
    pedido.save()

    messages.success(request, "Pedido cancelado com sucesso.")
    return redirect('payment:pedidos_pendentes')
