"""
Utilitários para monitoramento de segurança de pagamentos
"""
import logging
from django.utils import timezone
from django.utils.timezone import timedelta
from python_ipware import IpWare
from .models import TentativaFalsificacao
from utils.notifications import send_notification

logger = logging.getLogger(__name__)

# Instância do IpWare para obter IP do cliente
ipw = IpWare(precedence=("X_FORWARDED_FOR", "HTTP_X_FORWARDED_FOR"))


def registrar_tentativa_falsificacao(request, provedor, tipo_tentativa, detalhes=None):
    """
    Registra uma tentativa de falsificação de pagamento
    
    Args:
        request: Objeto request do Django
        provedor: 'Stripe' ou 'MercadoPago'
        tipo_tentativa: Tipo da tentativa (sem_assinatura, assinatura_falsa, etc)
        detalhes: Detalhes adicionais sobre a tentativa
    """
    try:
        ip_address, is_routable = ipw.get_client_ip(meta=request.META)
        if not ip_address:
            ip_address = '0.0.0.0'
        else:
            ip_address = str(ip_address)
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        tentativa = TentativaFalsificacao.objects.create(
            ip_address=ip_address,
            provedor=provedor,
            tipo_tentativa=tipo_tentativa,
            detalhes=detalhes or '',
            user_agent=user_agent[:500]  # Limita tamanho
        )
        
        # Verifica se deve enviar alerta
        if TentativaFalsificacao.deve_enviar_alerta(ip_address, limite=5, minutos=60):
            enviar_alerta_seguranca(ip_address, provedor, tentativa)
            tentativa.alerta_enviado = True
            tentativa.save(update_fields=['alerta_enviado'])
        
        logger.warning(
            f"Tentativa de falsificação registrada: {provedor} - {tipo_tentativa} - IP: {ip_address}"
        )
        
        return tentativa
    except Exception as e:
        logger.error(f"Erro ao registrar tentativa de falsificação: {e}")
        return None


def enviar_alerta_seguranca(ip_address, provedor, tentativa):
    """
    Envia alerta para staff sobre múltiplas tentativas de falsificação do mesmo IP
    """
    try:
        # Conta tentativas recentes
        ip_address_str = str(ip_address) if ip_address else None
        tentativas_recentes = TentativaFalsificacao.contar_tentativas_recentes(ip_address_str, minutos=60)
        
        # Conta tentativas totais nas últimas 24h
        cutoff_24h = timezone.now() - timedelta(hours=24)
        tentativas_24h = TentativaFalsificacao.objects.filter(
            ip_address=ip_address_str,
            data_tentativa__gte=cutoff_24h
        ).count()
        
        # Busca tipos de tentativas mais comuns
        from django.db.models import Count
        
        tipos_comuns = TentativaFalsificacao.objects.filter(
            ip_address=ip_address_str,
            data_tentativa__gte=cutoff_24h
        ).values('tipo_tentativa').annotate(
            count=Count('id')
        ).order_by('-count')[:3]
        
        tipos_str = ', '.join([f"{t['tipo_tentativa']} ({t['count']}x)" for t in tipos_comuns])
        
        mensagem = (
            f"🚨 ALERTA DE SEGURANÇA - Múltiplas tentativas de falsificação de pagamento detectadas!\n\n"
            f"IP: {ip_address}\n"
            f"Provedor: {provedor}\n"
            f"Tentativas (última hora): {tentativas_recentes}\n"
            f"Tentativas (últimas 24h): {tentativas_24h}\n"
            f"Tipos mais comuns: {tipos_str}\n"
            f"Última tentativa: {tentativa.tipo_tentativa}\n\n"
            f"Recomendação: Considere bloquear este IP se o padrão continuar."
        )
        
        send_notification(
            user=None,
            notification_type='staff',
            message=mensagem,
            created_by=None
        )
        
        logger.critical(
            f"ALERTA DE SEGURANÇA: {tentativas_recentes} tentativas de falsificação "
            f"do IP {ip_address} nas últimas 60 minutos"
        )
        
    except Exception as e:
        logger.error(f"Erro ao enviar alerta de segurança: {e}")


def obter_estatisticas_seguranca(ip_address=None, dias=7):
    """
    Obtém estatísticas de segurança de pagamentos
    
    Args:
        ip_address: IP específico (opcional)
        dias: Número de dias para analisar
    
    Returns:
        dict com estatísticas
    """
    from django.db.models import Count, Q
    
    cutoff = timezone.now() - timedelta(days=dias)
    queryset = TentativaFalsificacao.objects.filter(data_tentativa__gte=cutoff)
    
    if ip_address:
        queryset = queryset.filter(ip_address=str(ip_address))
    
    total = queryset.count()
    
    por_provedor = queryset.values('provedor').annotate(
        count=Count('id')
    ).order_by('-count')
    
    por_tipo = queryset.values('tipo_tentativa').annotate(
        count=Count('id')
    ).order_by('-count')
    
    ips_mais_ativos = queryset.values('ip_address').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return {
        'total_tentativas': total,
        'por_provedor': list(por_provedor),
        'por_tipo': list(por_tipo),
        'ips_mais_ativos': list(ips_mais_ativos),
        'periodo_dias': dias
    }


def reconciliar_pendentes_mercadopago(cutoff_minutes: int = 5) -> int:
    """
    Reconcilia pagamentos pendentes do Mercado Pago consultando o status no servidor.
    
    Args:
        cutoff_minutes: Minutos mínimos desde a criação para tentar conciliar
        
    Returns:
        Número de pagamentos reconciliados
    """
    try:
        import mercadopago
        from django.conf import settings
        from django.db import transaction
        from decimal import Decimal
        from .models import Pagamento
        from apps.lineage.wallet.utils import aplicar_compra_com_bonus
        
        # Verifica se Mercado Pago está configurado
        if not getattr(settings, 'MERCADO_PAGO_ACCESS_TOKEN', None):
            logger.warning("MERCADO_PAGO_ACCESS_TOKEN não configurado. Pulando reconciliação.")
            return 0
        
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        
        # Busca pagamentos pendentes criados há pelo menos cutoff_minutes minutos
        cutoff_time = timezone.now() - timedelta(minutes=cutoff_minutes)
        pagamentos_pendentes = Pagamento.objects.filter(
            status='pending',
            data_criacao__lte=cutoff_time
        ).select_related('pedido_pagamento', 'usuario')
        
        reconciliados = 0
        
        for pagamento in pagamentos_pendentes:
            pedido = pagamento.pedido_pagamento
            if not pedido or pedido.metodo != 'MercadoPago':
                continue
            
            try:
                # Consulta o Mercado Pago usando o ID do pagamento como external_reference
                search = sdk.merchant_order().search({'external_reference': str(pagamento.id)})
                
                if search.get('status') == 200:
                    results = (search.get('response') or {}).get('elements', [])
                    
                    for order in results:
                        pagamentos_mp = order.get('payments', [])
                        aprovado = any(p.get('status') == 'approved' for p in pagamentos_mp)
                        
                        if aprovado:
                            # Processa o pagamento aprovado
                            with transaction.atomic():
                                from apps.lineage.wallet.models import Wallet
                                wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                                
                                valor_total, valor_bonus, _ = aplicar_compra_com_bonus(
                                    wallet, Decimal(str(pagamento.valor)), 'MercadoPago'
                                )
                                
                                pagamento.status = 'paid'
                                pagamento.processado_em = timezone.now()
                                pagamento.save()
                                
                                pedido.bonus_aplicado = valor_bonus
                                pedido.total_creditado = valor_total
                                pedido.status = 'CONCLUÍDO'
                                pedido.save()

                                try:
                                    from django.urls import reverse
                                    from utils.push import send_push_to_staff_for_event, EVENT_ADMIN_DOACOES_COMPRAS
                                    send_push_to_staff_for_event(
                                        EVENT_ADMIN_DOACOES_COMPRAS,
                                        username=pedido.usuario.username,
                                        valor=str(pedido.valor_pago),
                                        url=reverse('dashboard'),
                                        async_send=True,
                                    )
                                except Exception:
                                    pass

                                reconciliados += 1
                                logger.info(f"Pagamento {pagamento.id} reconciliado com sucesso")
                            break
                            
            except Exception as e:
                logger.error(f"Erro ao reconciliar pagamento {pagamento.id}: {e}")
                continue
        
        if reconciliados > 0:
            logger.info(f"Reconciliação concluída: {reconciliados} pagamento(s) reconciliado(s)")
        
        return reconciliados
        
    except Exception as e:
        logger.error(f"Erro ao reconciliar pagamentos pendentes do Mercado Pago: {e}")
        return 0
