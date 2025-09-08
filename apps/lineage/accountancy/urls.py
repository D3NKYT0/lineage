from django.urls import path
from . import views


app_name = "accountancy"


urlpatterns = [
    path('', views.dashboard_accountancy, name='dashboard'),
    path('balance-report/', views.relatorio_saldo_usuarios, name='relatorio_saldo'),
    path('cash-flow-report/', views.relatorio_fluxo_caixa, name='relatorio_fluxo_caixa'),
    path('orders-payments-report/', views.relatorio_pedidos_pagamentos, name='relatorio_pedidos_pagamentos'),
    path('wallet-reconciliation-report/', views.relatorio_reconciliacao_wallet, name='relatorio_reconciliacao_wallet'),
]
