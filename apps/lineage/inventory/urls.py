from django.urls import path
from . import views


app_name = "inventory"


urlpatterns = [
    path('withdraw/', views.retirar_item_servidor, name='retirar_item'),
    path('insert-item/<str:char_name>/<int:item_id>/', views.inserir_item_servidor, name='inserir_item'),
    path('trade/', views.trocar_item_com_jogador, name='trocar_item'),
    path('dashboard/', views.inventario_dashboard, name='inventario_dashboard'),
    path('global/', views.inventario_global, name='inventario_global'),
    path('transfer-to-bag/<str:char_name>/<int:item_id>/', views.transferir_para_bag, name='transferir_para_bag'),
    path('delete-obsolete/<str:character_name>/', views.deletar_inventario_obsoleto, name='deletar_inventario_obsoleto'),

    path('api/item-image/<int:item_id>/', views.get_item_image_url, name='get_item_image_url'),
]
