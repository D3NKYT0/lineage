from django.urls import path
from . import views


app_name = "reports"


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('inventory/', views.relatorio_movimentacoes_inventario, name='relatorio_movimentacoes_inventario'),
    path('auctions/', views.relatorio_leiloes, name='relatorio_leiloes'),
    path('purchases/', views.relatorio_compras, name='relatorio_compras'),
    path('social/', views.relatorio_rede_social, name='relatorio_rede_social'),
]
