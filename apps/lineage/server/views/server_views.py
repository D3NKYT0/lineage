from django.shortcuts import render, redirect
from apps.main.home.decorator import conditional_otp_required
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Apoiador
from apps.lineage.shop.models import ShopPurchase, PromotionCode
from django.contrib import messages
from ..forms import ApoiadorForm
from django.db.models import Sum
from django.utils import timezone

from ..forms import SolicitarComissaoForm, ImagemApoiadorForm
from ..utils.apoiador import pagar_comissao, calcular_valor_disponivel
from decimal import Decimal


@conditional_otp_required
def painel_apoiador(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
    except Apoiador.DoesNotExist:
        return render(request, 'apoiadores/nao_apoiador.html')

    # Status expirado permite reenviar o formulário
    if apoiador.status == 'expirado':
        return render(request, 'apoiadores/expirado.html', {'apoiador': apoiador})

    if apoiador.status == 'pendente':
        return render(request, 'apoiadores/pendente.html', {'apoiador': apoiador})
    elif apoiador.status == 'rejeitado':
        return render(request, 'apoiadores/rejeitado.html', {'apoiador': apoiador})
    elif apoiador.status != 'aprovado':
        return render(request, 'apoiadores/nao_apoiador.html')

    # Painel de apoiador aprovado
    compras = (
        ShopPurchase.objects
        .filter(apoiador=apoiador)
        .select_related('user')
        .only('user__username', 'character_name', 'total_pago', 'data_compra')
        .order_by('-data_compra')
    )

    total_vendas = compras.aggregate(total=Sum('total_pago'))['total'] or 0
    total_usuarios = compras.values('user').distinct().count()

    try:
        cupom = PromotionCode.objects.get(apoiador=apoiador, ativo=True)
    except PromotionCode.DoesNotExist:
        cupom = None

    return render(request, 'apoiadores/painel.html', {
        'apoiador': apoiador,
        'compras': compras,
        'total_vendas': total_vendas,
        'total_usuarios': total_usuarios,
        'cupom': cupom
    })


@conditional_otp_required
def formulario_apoiador(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
        if apoiador.status == 'aprovado' or apoiador.status == 'pendente':
            messages.info(request, "Você já possui uma solicitação ativa.")
            return redirect('server:painel_apoiador')
    except Apoiador.DoesNotExist:
        apoiador = None

    if request.method == "POST":
        form = ApoiadorForm(request.POST, request.FILES, instance=apoiador)

        if form.is_valid():
            novo_apoiador = form.save(commit=False)
            novo_apoiador.user = request.user
            novo_apoiador.status = 'pendente'  # Sempre reinicia como pendente
            novo_apoiador.save()

            messages.success(request, "Sua nova solicitação foi enviada com sucesso! Aguarde análise.")
            return redirect('server:painel_apoiador')
        else:
            messages.error(request, "Ocorreu um erro ao enviar a solicitação. Verifique os dados.")
    else:
        form = ApoiadorForm(instance=apoiador)

    return render(request, 'apoiadores/formulario_apoiador.html', {'form': form})


@staff_member_required
def painel_staff(request):
    if request.method == 'POST':
        apoiador_id = request.POST.get('apoiador_id')
        acao = request.POST.get('acao')
        desconto_percentual = request.POST.get('desconto_percentual')

        try:
            apoiador = Apoiador.objects.get(id=apoiador_id)

            if acao == 'aceitar':
                apoiador.status = 'aprovado'
                apoiador.save()

                if desconto_percentual:
                    desconto_percentual = float(desconto_percentual)
                else:
                    messages.error(request, 'A porcentagem do cupom é obrigatória.')
                    return redirect('server:painel_staff')

                promocao, created = PromotionCode.objects.get_or_create(
                    apoiador=apoiador,
                    defaults={
                        'codigo': f"{str(apoiador.nome_publico).upper().replace(' ', '_').replace('-', '_')}-{int(desconto_percentual)}",
                        'desconto_percentual': desconto_percentual,
                        'ativo': True,
                        'validade': timezone.now() + timezone.timedelta(days=30)
                    }
                )

                # Se o cupom já existia, atualize o desconto
                if not created:
                    promocao.desconto_percentual = desconto_percentual
                    promocao.validade = timezone.now() + timezone.timedelta(days=30)
                    promocao.ativo = True
                    promocao.save()

                messages.success(request, f'Apoiador {apoiador.nome_publico} aprovado e cupom gerado ou atualizado!')

            elif acao == 'rejeitar':
                # Alterar o status para 'rejeitado'
                apoiador.status = 'rejeitado'
                apoiador.save()

                messages.info(request, f'Apoiador {apoiador.nome_publico} rejeitado.')

        except Apoiador.DoesNotExist:
            messages.error(request, 'Apoiador não encontrado.')

    # Buscar todos os apoiadores para estatísticas
    solicitacoes_pendentes = Apoiador.objects.filter(status='pendente').count()
    apoiadores_aprovados = Apoiador.objects.filter(status='aprovado').count()
    solicitacoes_rejeitadas = Apoiador.objects.filter(status='rejeitado').count()
    
    # Buscar todos os apoiadores para a lista
    apoiadores = Apoiador.objects.all().order_by('-user__date_joined')
    
    return render(request, 'apoiadores/painel_staff.html', {
        'solicitacoes_pendentes': solicitacoes_pendentes,
        'apoiadores_aprovados': apoiadores_aprovados,
        'solicitacoes_rejeitadas': solicitacoes_rejeitadas,
        'apoiadores': apoiadores
    })


@conditional_otp_required
def solicitar_comissao(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
    except Apoiador.DoesNotExist:
        return redirect('server:painel_apoiador')

    if apoiador.status != 'aprovado':
        messages.error(request, "Seu cadastro não está aprovado para solicitar comissão.")
        return redirect('server:painel_apoiador')

    # Valor disponível para saque
    valor_disponivel = calcular_valor_disponivel(apoiador)

    if request.method == 'POST':
        form = SolicitarComissaoForm(request.POST)
        if form.is_valid():
            valor = form.cleaned_data['valor']

            if valor > valor_disponivel:
                messages.error(request, f'O valor solicitado excede o disponível (R${valor_disponivel}).')
            elif valor <= 0:
                messages.error(request, "O valor solicitado deve ser maior que zero.")
            else:
                pagar_comissao(apoiador, Decimal(valor))
                messages.success(request, f'Comissão de R${valor} solicitada com sucesso!')
                return redirect('server:painel_apoiador')
    else:
        form = SolicitarComissaoForm()

    return render(request, 'apoiadores/solicitar_comissao.html', {
        'form': form,
        'valor_disponivel': valor_disponivel
    })


@conditional_otp_required
def editar_imagem_apoiador(request):
    try:
        apoiador = Apoiador.objects.get(user=request.user)
    except Apoiador.DoesNotExist:
        return redirect('server:painel_apoiador')  # ou uma página de erro

    if request.method == 'POST':
        form = ImagemApoiadorForm(request.POST, request.FILES, instance=apoiador)
        if form.is_valid():
            form.save()
            return redirect('server:painel_apoiador')
    else:
        form = ImagemApoiadorForm(instance=apoiador)

    return render(request, 'apoiadores/editar_imagem.html', {'form': form})


@staff_member_required
def aprovar_apoiador(request, apoiador_id):
    if request.method == 'POST':
        try:
            apoiador = Apoiador.objects.get(id=apoiador_id)
            apoiador.status = 'aprovado'
            apoiador.save()
            
            # Criar cupom padrão de 10%
            promocao, created = PromotionCode.objects.get_or_create(
                apoiador=apoiador,
                defaults={
                    'codigo': f"{str(apoiador.nome_publico).upper().replace(' ', '_').replace('-', '_')}-10",
                    'desconto_percentual': 10,
                    'ativo': True,
                    'validade': timezone.now() + timezone.timedelta(days=30)
                }
            )
            
            if not created:
                promocao.desconto_percentual = 10
                promocao.validade = timezone.now() + timezone.timedelta(days=30)
                promocao.ativo = True
                promocao.save()
            
            messages.success(request, f'Apoiador {apoiador.nome_publico} aprovado com sucesso!')
        except Apoiador.DoesNotExist:
            messages.error(request, 'Apoiador não encontrado.')
    
    return redirect('server:painel_staff')


@staff_member_required
def rejeitar_apoiador(request, apoiador_id):
    if request.method == 'POST':
        try:
            apoiador = Apoiador.objects.get(id=apoiador_id)
            apoiador.status = 'rejeitado'
            apoiador.save()
            messages.info(request, f'Apoiador {apoiador.nome_publico} rejeitado.')
        except Apoiador.DoesNotExist:
            messages.error(request, 'Apoiador não encontrado.')
    
    return redirect('server:painel_staff')


@staff_member_required
def detalhes_apoiador(request, apoiador_id):
    try:
        apoiador = Apoiador.objects.get(id=apoiador_id)
        
        # Buscar compras relacionadas
        compras = ShopPurchase.objects.filter(apoiador=apoiador).order_by('-data_compra')
        total_vendas = compras.aggregate(total=Sum('total_pago'))['total'] or 0
        total_usuarios = compras.values('user').distinct().count()
        
        # Buscar cupom ativo
        try:
            cupom = PromotionCode.objects.get(apoiador=apoiador, ativo=True)
        except PromotionCode.DoesNotExist:
            cupom = None
        
        return render(request, 'apoiadores/detalhes_apoiador.html', {
            'apoiador': apoiador,
            'compras': compras,
            'total_vendas': total_vendas,
            'total_usuarios': total_usuarios,
            'cupom': cupom
        })
    except Apoiador.DoesNotExist:
        messages.error(request, 'Apoiador não encontrado.')
        return redirect('server:painel_staff')
