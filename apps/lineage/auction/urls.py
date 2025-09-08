from django.urls import path
from . import views


app_name = "auction"


urlpatterns = [
    path('', views.listar_leiloes, name='listar_leiloes'),
    path('create/', views.criar_leilao, name='criar_leilao'),
    path('bid/<int:auction_id>/', views.fazer_lance, name='fazer_lance'),
    path('finish/<int:auction_id>/', views.encerrar_leilao, name='encerrar_leilao'),
    path('cancel/<int:auction_id>/', views.cancelar_leilao, name='cancelar_leilao'),
]
