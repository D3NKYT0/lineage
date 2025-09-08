from django.urls import path
from . import views, manager_views

app_name = "shop"

urlpatterns = [
    path('', views.shop_home, name='shop_home'),

    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add-item/<int:item_id>/', views.add_item_to_cart, name='add_item_to_cart'),
    path('cart/add-package/<int:package_id>/', views.add_package_to_cart, name='add_package_to_cart'),
    path('cart/apply-promo/', views.apply_promo_code, name='apply_promo_code'),
    path('cart/toggle-bonus/', views.toggle_bonus_usage, name='toggle_bonus_usage'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/remove/item/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('cart/remove/package/<int:package_id>/', views.remove_cart_package, name='remove_cart_package'),
    
    path('purchases/', views.purchase_history, name='purchase_history'),

    path('manager/dashboard/', manager_views.dashboard, name='dashboard'),
    path('manager/promotions/', manager_views.promotions, name='promotions'),
    path('manager/items/', manager_views.items, name='items'),
    path('manager/packages/', manager_views.packages, name='packages'),
    path('manager/package/edit/<int:package_id>/', manager_views.edit_package, name='edit_package'),
    path('manager/package/add_item/<int:package_id>/', manager_views.add_item_to_package, name='add_item_to_package'),
    path('manager/package/remove_item/<int:item_id>/', manager_views.remove_item_from_package, name='remove_item_from_package'),
]
