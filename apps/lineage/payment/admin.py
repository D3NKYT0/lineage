from django.contrib import admin
from django.utils.html import format_html
from .models import PedidoPagamento, Pagamento, WebhookLog, TentativaFalsificacao
from core.admin import BaseModelAdmin
from django.template.response import TemplateResponse


@admin.register(PedidoPagamento)
class PedidoPagamentoAdmin(BaseModelAdmin):
    list_display = ('usuario', 'valor_pago', 'bonus_aplicado', 'total_creditado', 'metodo', 'status', 'data_criacao')
    list_filter = ('status', 'metodo', 'data_criacao')
    search_fields = ('usuario__username', 'metodo')
    readonly_fields = ('usuario', 'valor_pago', 'moedas_geradas', 'metodo', 'data_criacao', 'bonus_aplicado', 'total_creditado')
    
    fieldsets = (
        ('Informações do Pedido', {
            'fields': ('usuario', 'valor_pago', 'metodo', 'status', 'data_criacao')
        }),
        ('Bônus e Totais', {
            'fields': ('bonus_aplicado', 'total_creditado'),
            'description': 'Informações sobre bônus aplicados e total creditado'
        }),
        ('Campos Legados', {
            'fields': ('moedas_geradas',),
            'description': 'Campo mantido para compatibilidade'
        }),
    )

    actions = ['confirmar_pagamentos']

    @admin.action(description='Confirmar pagamentos selecionados')
    def confirmar_pagamentos(self, request, queryset):
        import logging
        from django.utils import timezone
        from django.contrib import messages
        from .models import Pagamento

        logger = logging.getLogger(__name__)
        
        # Tela de confirmação customizada
        if 'apply' not in request.POST:
            context = {
                'queryset': queryset,
                'opts': self.model._meta,
                'app_label': self.model._meta.app_label,
                'action': 'confirmar_pagamentos',
                'title': 'Confirmar pagamentos selecionados',
                'total': queryset.count(),
            }
            return TemplateResponse(request, 'admin/payment/confirmar_pagamentos.html', context)

        processados = 0
        ja_confirmados = 0
        erros = 0
        erros_detalhes = []

        for pedido in queryset.select_related('usuario'):
            # Verifica se já está confirmado
            if pedido.status == 'CONFIRMADO' or pedido.status == 'CONCLUÍDO':
                ja_confirmados += 1
                logger.debug(f"Pedido {pedido.id} ignorado: já está com status '{pedido.status}'")
                continue

            try:
                # Confirma o pedido e aplica os créditos/bônus (marca no histórico o admin)
                pedido.confirmar_pagamento(actor=request.user)
                
                # Marca como CONCLUÍDO para manter consistência com outros fluxos
                pedido.status = 'CONCLUÍDO'
                pedido.save()
                
                # Também marca o Pagamento associado como 'paid' para evitar reprocessamento via webhook
                pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()
                if pagamento and pagamento.status != 'paid':
                    pagamento.status = 'paid'
                    pagamento.processado_em = timezone.now()
                    pagamento.save()
                
                processados += 1
                logger.info(f"Pedido {pedido.id} confirmado e concluído com sucesso. Valor: R${pedido.valor_pago}, Bônus: R${pedido.bonus_aplicado}")
            except Exception as e:
                erros += 1
                erro_msg = f"Pedido {pedido.id}: {str(e)}"
                erros_detalhes.append(erro_msg)
                logger.error(f"Erro ao confirmar pedido {pedido.id}: {str(e)}", exc_info=True)

        # Mensagens informativas
        mensagens = []
        if processados > 0:
            mensagens.append(f"{processados} pagamento(s) confirmado(s) e concluído(s) com sucesso.")
        if ja_confirmados > 0:
            mensagens.append(f"{ja_confirmados} pedido(s) já estava(m) confirmado(s) ou concluído(s) e foi(ram) ignorado(s).")
        if erros > 0:
            mensagens.append(f"{erros} pedido(s) com erro durante o processamento.")
            # Mostra detalhes dos erros apenas se houver poucos
            if erros <= 5:
                for detalhe in erros_detalhes:
                    messages.error(request, detalhe)
            else:
                messages.error(request, f"Vários erros ocorreram. Verifique os logs para detalhes.")
        
        if mensagens:
            self.message_user(request, " ".join(mensagens))
        else:
            self.message_user(request, "Nenhum pagamento foi processado. Verifique os critérios de seleção.")

    class Media:
        js = ('admin/js/pedido_pagamento_admin.js',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')


@admin.register(Pagamento)
class PagamentoAdmin(BaseModelAdmin):
    list_display = ('id', 'usuario', 'valor', 'status', 'transaction_code', 'pedido_link', 'data_criacao')
    list_filter = ('status', 'data_criacao')
    search_fields = ('usuario__username', 'transaction_code')
    ordering = ('-data_criacao',)
    readonly_fields = ('data_criacao', 'transaction_code')

    actions = ['reconciliar_mercadopago', 'processar_aprovados', 'exportar_csv']

    fieldsets = (
        (None, {
            'fields': ('usuario', 'valor', 'status', 'transaction_code', 'pedido_pagamento', 'data_criacao')
        }),
    )

    def pedido_link(self, obj):
        if obj.pedido_pagamento:
            return format_html('<a href="/admin/payment/pedidopagamento/{}/change/">Ver Pedido</a>', obj.pedido_pagamento.id)
        return '-'
    pedido_link.short_description = "Pedido"

    @admin.action(description='Reconciliar pagamentos pendentes (Mercado Pago)')
    def reconciliar_mercadopago(self, request, queryset):
        import logging
        import mercadopago
        from django.utils import timezone
        from django.contrib import messages
        from django.db import transaction
        from apps.lineage.wallet.utils import aplicar_compra_com_bonus
        from decimal import Decimal
        from django.conf import settings

        logger = logging.getLogger(__name__)
        
        # Inicializa SDK do Mercado Pago
        try:
            access_token = getattr(settings, 'MERCADO_PAGO_ACCESS_TOKEN', None)
            if not access_token:
                self.message_user(request, "Erro: MERCADO_PAGO_ACCESS_TOKEN não configurado.", level=messages.ERROR)
                return
            sdk = mercadopago.SDK(access_token)
        except Exception as e:
            logger.error(f"Erro ao inicializar SDK do Mercado Pago: {str(e)}", exc_info=True)
            self.message_user(request, f"Erro ao inicializar SDK do Mercado Pago: {str(e)}", level=messages.ERROR)
            return

        reconciliados = 0
        ignorados_status = 0
        ignorados_metodo = 0
        nao_encontrados = 0
        nao_aprovados = 0
        erros = 0
        erros_detalhes = []

        for pagamento in queryset.select_related('pedido_pagamento', 'usuario'):
            # Verifica status do pagamento
            if pagamento.status != 'pending':
                ignorados_status += 1
                logger.debug(f"Pagamento {pagamento.id} ignorado: status '{pagamento.status}' (esperado: 'pending')")
                continue
            
            # Verifica pedido associado
            pedido = pagamento.pedido_pagamento
            if not pedido:
                ignorados_metodo += 1
                logger.warning(f"Pagamento {pagamento.id} ignorado: sem pedido associado")
                continue
            
            if pedido.metodo != 'MercadoPago':
                ignorados_metodo += 1
                logger.debug(f"Pagamento {pagamento.id} ignorado: método '{pedido.metodo}' (esperado: 'MercadoPago')")
                continue

            try:
                # Busca no Mercado Pago
                search = sdk.merchant_order().search({'external_reference': str(pagamento.id)})
                
                if search.get('status') != 200:
                    nao_encontrados += 1
                    logger.warning(f"Pagamento {pagamento.id}: resposta do Mercado Pago com status {search.get('status')}")
                    continue
                
                results = (search.get('response') or {}).get('elements', [])
                if not results:
                    nao_encontrados += 1
                    logger.debug(f"Pagamento {pagamento.id}: nenhuma ordem encontrada no Mercado Pago")
                    continue
                
                # Verifica se algum pagamento foi aprovado
                aprovado = False
                for order in results:
                    pagamentos_mp = order.get('payments', [])
                    if any(p.get('status') == 'approved' for p in pagamentos_mp):
                        aprovado = True
                        break
                
                if not aprovado:
                    nao_aprovados += 1
                    logger.debug(f"Pagamento {pagamento.id}: nenhum pagamento aprovado encontrado no Mercado Pago")
                    continue
                
                # Processa o pagamento aprovado
                with transaction.atomic():
                    wallet, _ = pedido.usuario.wallet_set.get_or_create(usuario=pagamento.usuario)
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
                    reconciliados += 1
                    logger.info(f"Pagamento {pagamento.id} reconciliado com sucesso. Valor: R${pagamento.valor}, Bônus: R${valor_bonus}")
                    
            except Exception as e:
                erros += 1
                erro_msg = f"Pagamento {pagamento.id}: {str(e)}"
                erros_detalhes.append(erro_msg)
                logger.error(f"Erro ao reconciliar pagamento {pagamento.id}: {str(e)}", exc_info=True)

        # Mensagens informativas
        mensagens = []
        if reconciliados > 0:
            mensagens.append(f"{reconciliados} pagamento(s) reconciliado(s) com sucesso.")
        if ignorados_status > 0:
            mensagens.append(f"{ignorados_status} pagamento(s) ignorado(s) por status diferente de 'pending'.")
        if ignorados_metodo > 0:
            mensagens.append(f"{ignorados_metodo} pagamento(s) ignorado(s) por pedido ausente ou método diferente de 'MercadoPago'.")
        if nao_encontrados > 0:
            mensagens.append(f"{nao_encontrados} pagamento(s) não encontrado(s) no Mercado Pago.")
        if nao_aprovados > 0:
            mensagens.append(f"{nao_aprovados} pagamento(s) encontrado(s) mas não aprovado(s) no Mercado Pago.")
        if erros > 0:
            mensagens.append(f"{erros} pagamento(s) com erro durante a reconciliação.")
            # Mostra detalhes dos erros apenas se houver poucos
            if erros <= 5:
                for detalhe in erros_detalhes:
                    messages.error(request, detalhe)
            else:
                messages.error(request, f"Vários erros ocorreram. Verifique os logs para detalhes.")
        
        if mensagens:
            self.message_user(request, " ".join(mensagens))
        else:
            self.message_user(request, "Nenhum pagamento foi reconciliado. Verifique os critérios de seleção.")

    @admin.action(description='Processar pagamentos aprovados (creditar e concluir)')
    def processar_aprovados(self, request, queryset):
        import logging
        from django.utils import timezone
        from decimal import Decimal
        from django.db import transaction
        from django.contrib import messages
        from apps.lineage.wallet.models import Wallet
        from apps.lineage.wallet.utils import aplicar_compra_com_bonus

        logger = logging.getLogger(__name__)
        processados = 0
        ignorados_status = 0
        ignorados_pedido = 0
        erros = 0
        erros_detalhes = []

        for pagamento in queryset.select_related('pedido_pagamento', 'usuario'):
            # Verifica status do pagamento
            if pagamento.status != 'approved':
                ignorados_status += 1
                logger.debug(f"Pagamento {pagamento.id} ignorado: status '{pagamento.status}' (esperado: 'approved')")
                continue
            
            # Verifica pedido associado
            pedido = pagamento.pedido_pagamento
            if not pedido:
                ignorados_pedido += 1
                logger.warning(f"Pagamento {pagamento.id} ignorado: sem pedido associado")
                continue
            
            if pedido.status != 'PENDENTE':
                ignorados_pedido += 1
                logger.debug(f"Pagamento {pagamento.id} ignorado: pedido {pedido.id} com status '{pedido.status}' (esperado: 'PENDENTE')")
                continue
            
            # Tenta processar o pagamento
            try:
                with transaction.atomic():
                    wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                    metodo = pedido.metodo if pedido else 'MercadoPago'
                    valor_total, valor_bonus, _ = aplicar_compra_com_bonus(
                        wallet, Decimal(str(pagamento.valor)), metodo
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
                    processados += 1
                    logger.info(f"Pagamento {pagamento.id} processado com sucesso. Valor: R${pagamento.valor}, Bônus: R${valor_bonus}")
            except Exception as e:
                erros += 1
                erro_msg = f"Pagamento {pagamento.id}: {str(e)}"
                erros_detalhes.append(erro_msg)
                logger.error(f"Erro ao processar pagamento {pagamento.id}: {str(e)}", exc_info=True)

        # Mensagens informativas
        mensagens = []
        if processados > 0:
            mensagens.append(f"{processados} pagamento(s) processado(s) com sucesso.")
        if ignorados_status > 0:
            mensagens.append(f"{ignorados_status} pagamento(s) ignorado(s) por status diferente de 'approved'.")
        if ignorados_pedido > 0:
            mensagens.append(f"{ignorados_pedido} pagamento(s) ignorado(s) por pedido ausente ou status diferente de 'PENDENTE'.")
        if erros > 0:
            mensagens.append(f"{erros} pagamento(s) com erro durante o processamento.")
            # Mostra detalhes dos erros apenas se houver poucos
            if erros <= 5:
                for detalhe in erros_detalhes:
                    messages.error(request, detalhe)
            else:
                messages.error(request, f"Vários erros ocorreram. Verifique os logs para detalhes.")
        
        if mensagens:
            self.message_user(request, " ".join(mensagens))
        else:
            self.message_user(request, "Nenhum pagamento foi processado. Verifique os critérios de seleção.")

    @admin.action(description='Exportar CSV dos pagamentos selecionados')
    def exportar_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pagamentos.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Usuario', 'Valor', 'Status', 'Transaction Code', 'Pedido ID', 'Criado em', 'Processado em'])
        for p in queryset.select_related('usuario', 'pedido_pagamento'):
            writer.writerow([
                p.id,
                getattr(p.usuario, 'username', ''),
                f"{p.valor:.2f}",
                p.status,
                p.transaction_code or '',
                getattr(p.pedido_pagamento, 'id', ''),
                p.data_criacao.isoformat() if p.data_criacao else '',
                p.processado_em.isoformat() if getattr(p, 'processado_em', None) else '',
            ])
        return response


@admin.register(WebhookLog)
class WebhookLogAdmin(BaseModelAdmin):
    list_display = ('id', 'provedor', 'tipo', 'data_id', 'pagamento_relacionado', 'status_evento', 'recebido_em')
    search_fields = ('tipo', 'data_id', 'payload__data__object__metadata__pagamento_id', 'payload__metadata__pagamento_id')
    list_filter = ('tipo', 'recebido_em')
    readonly_fields = ('tipo', 'data_id', 'payload', 'recebido_em')
    ordering = ('-recebido_em',)

    def provedor(self, obj):
        # Heurística simples: Stripe usa tipos com ponto (ex.: checkout.session.completed)
        # MP usa tipos planos (payment, merchant_order, ...)
        try:
            return 'Stripe' if (obj.tipo and '.' in obj.tipo) else 'MercadoPago'
        except Exception:
            return '-'
    provedor.short_description = 'Provedor'

    def pagamento_relacionado(self, obj):
        # Tenta extrair pagamento_id de diferentes formatos de payload
        p = obj.payload or {}
        try:
            # Stripe (checkout.session.*)
            meta = (((p.get('data') or {}).get('object') or {}).get('metadata') or {})
            pid = meta.get('pagamento_id')
            if pid:
                return pid
            # Stripe (payment_intent.*)
            meta = ((p.get('data') or {}).get('object') or {}).get('metadata') or {}
            pid = meta.get('pagamento_id')
            if pid:
                return pid
            # Mercado Pago (fallback de sucesso com payload completo)
            pid = (p.get('metadata') or {}).get('pagamento_id')
            if pid:
                return pid
        except Exception:
            pass
        return '-'
    pagamento_relacionado.short_description = 'Pagamento ID'

    def status_evento(self, obj):
        p = obj.payload or {}
        try:
            # Stripe session
            data_object = (p.get('data') or {}).get('object') or {}
            if 'payment_status' in data_object:
                return data_object.get('payment_status') or data_object.get('status') or '-'
            # Stripe PI
            if data_object.get('object') == 'payment_intent':
                return data_object.get('status') or '-'
            # Mercado Pago (fallbacks armazenam status direto)
            if 'status' in p:
                return p.get('status')
        except Exception:
            pass
        return '-'
    status_evento.short_description = 'Status'

    def has_add_permission(self, request):
        return False  # impede a criação manual

    def has_change_permission(self, request, obj=None):
        return False  # impede a edição

    def has_delete_permission(self, request, obj=None):
        return False  # impede a exclusão


@admin.register(TentativaFalsificacao)
class TentativaFalsificacaoAdmin(BaseModelAdmin):
    list_display = ('id', 'ip_address', 'provedor', 'tipo_tentativa', 'alerta_enviado', 'data_tentativa')
    list_filter = ('provedor', 'tipo_tentativa', 'alerta_enviado', 'data_tentativa')
    search_fields = ('ip_address', 'detalhes', 'user_agent')
    readonly_fields = ('ip_address', 'provedor', 'tipo_tentativa', 'detalhes', 'user_agent', 'data_tentativa', 'alerta_enviado')
    ordering = ('-data_tentativa',)
    
    fieldsets = (
        ('Informações da Tentativa', {
            'fields': ('ip_address', 'provedor', 'tipo_tentativa', 'data_tentativa')
        }),
        ('Detalhes', {
            'fields': ('detalhes', 'user_agent', 'alerta_enviado'),
            'description': 'Informações adicionais sobre a tentativa de falsificação'
        }),
    )
    
    def has_add_permission(self, request):
        return False  # impede a criação manual
    
    def has_change_permission(self, request, obj=None):
        return False  # impede a edição (apenas visualização)
    
    actions = ['marcar_alerta_enviado', 'obter_estatisticas_ip']
    
    @admin.action(description='Marcar alertas como enviados')
    def marcar_alerta_enviado(self, request, queryset):
        import logging
        from django.contrib import messages
        
        logger = logging.getLogger(__name__)
        
        try:
            atualizados = queryset.update(alerta_enviado=True)
            logger.info(f"{atualizados} tentativa(s) de falsificação marcada(s) com alerta enviado pelo admin {request.user.username}")
            self.message_user(request, f"{atualizados} tentativa(s) marcada(s) com alerta enviado.")
        except Exception as e:
            logger.error(f"Erro ao marcar alertas como enviados: {str(e)}", exc_info=True)
            self.message_user(request, f"Erro ao marcar alertas: {str(e)}", level=messages.ERROR)
    
    @admin.action(description='Ver estatísticas do IP')
    def obter_estatisticas_ip(self, request, queryset):
        import logging
        from ..utils import obter_estatisticas_seguranca
        from django.contrib import messages
        
        logger = logging.getLogger(__name__)
        
        if queryset.count() != 1:
            messages.warning(request, "Selecione apenas uma tentativa para ver estatísticas do IP.")
            return
        
        tentativa = queryset.first()
        if not tentativa or not tentativa.ip_address:
            messages.error(request, "Tentativa selecionada não possui endereço IP válido.")
            return
        
        try:
            stats = obter_estatisticas_seguranca(ip_address=tentativa.ip_address, dias=7)
            
            if not stats:
                messages.warning(request, f"Nenhuma estatística encontrada para o IP {tentativa.ip_address}.")
                return
            
            provedores_str = ', '.join([f"{p['provedor']}: {p['count']}" for p in stats.get('por_provedor', [])])
            tipos_str = ', '.join([f"{t['tipo_tentativa']}: {t['count']}" for t in stats.get('por_tipo', [])[:5]])
            
            mensagem = (
                f"Estatísticas do IP {tentativa.ip_address} (últimos 7 dias):\n"
                f"Total de tentativas: {stats.get('total_tentativas', 0)}\n"
                f"Por provedor: {provedores_str or 'Nenhum'}\n"
                f"Tipos mais comuns: {tipos_str or 'Nenhum'}"
            )
            
            messages.info(request, mensagem)
            logger.info(f"Estatísticas do IP {tentativa.ip_address} consultadas pelo admin {request.user.username}")
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do IP {tentativa.ip_address}: {str(e)}", exc_info=True)
            messages.error(request, f"Erro ao obter estatísticas: {str(e)}")
