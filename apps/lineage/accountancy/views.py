from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from apps.main.home.models import User
import json

from .reports.saldo import saldo_usuario
from .reports.fluxo_caixa import fluxo_caixa_por_dia
from .reports.pedidos_pagamentos import pedidos_pagamentos_resumo
from .reports.reconciliacao_wallet import reconciliacao_wallet_transacoes


@staff_member_required
def relatorio_saldo_usuarios(request):
    usuarios = User.objects.all()
    relatorio = []

    for usuario in usuarios:
        info = saldo_usuario(usuario)
        relatorio.append({
            'usuario': usuario.username,
            **info
        })

    return render(request, 'accountancy/relatorio_saldo.html', {
        'relatorio': relatorio
    })


@staff_member_required
def relatorio_fluxo_caixa(request):
    relatorio = fluxo_caixa_por_dia()

    labels = [str(item['data'].strftime('%d/%m')) for item in relatorio]
    entradas = [float(item['entradas']) for item in relatorio]
    saidas = [float(item['saidas']) for item in relatorio]
    saldos = [float(item['saldo']) for item in relatorio]

    labels.reverse()
    entradas.reverse()
    saidas.reverse()
    saldos.reverse()

    context = {
        'labels': json.dumps(labels),
        'entradas': json.dumps(entradas),
        'saidas': json.dumps(saidas),
        'saldos': json.dumps(saldos),
        'relatorio': relatorio,
    }

    return render(request, 'accountancy/relatorio_fluxo_caixa.html', context)


@staff_member_required
def relatorio_pedidos_pagamentos(request):
    relatorio = pedidos_pagamentos_resumo()
    return render(request, 'accountancy/relatorio_pedidos_pagamentos.html', {
        'relatorio': relatorio
    })


@staff_member_required
def relatorio_reconciliacao_wallet(request):
    relatorio = reconciliacao_wallet_transacoes()
    return render(request, 'accountancy/relatorio_reconciliacao_wallet.html', {
        'relatorio': relatorio
    })


@staff_member_required
def dashboard_accountancy(request):
    return render(request, 'accountancy/dashboard.html')
