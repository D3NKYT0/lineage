from django.urls import path
from .views import views, manager_box_views, battle_pass, economy_game_view


app_name = "games"


urlpatterns = [
    path('buy-tokens/', views.comprar_fichas, name='comprar_fichas'),

    path('roulette/', views.roulette_page, name='roulette_page'),
    path('roulette/spin-ajax/', views.spin_ajax, name='spin_ajax'),
    
    path('bag/dashboard/', views.bag_dashboard, name='bag_dashboard'),
    path('bag/transfer/', views.transferir_item_bag, name='transferir_item_bag'),
    path('bag/empty/', views.esvaziar_bag_para_inventario, name='esvaziar_bag_para_inventario'),

    path('box/dashboard/', views.box_dashboard_view, name='box_user_dashboard'),
    path('box/opening/', views.box_opening_home, name='box_opening_home'),
    path('box/buy-and-open/<int:box_type_id>/', views.buy_and_open_box_view, name='box_buy_and_open'),
    path('box/open/<int:box_id>/', views.open_box_view, name='box_user_open_box'),

    path('box/manager/dashboard/', manager_box_views.dashboard, name='box_manager_dashboard'),
    path('box/manager/boxes/', manager_box_views.box_list_view, name='box_list'),
    path('box/manager/box/create/', manager_box_views.box_create_view, name='box_create'),
    path('box/manager/box/edit/<int:pk>/', manager_box_views.box_edit_view, name='box_edit'),
    path('box/manager/box/delete/<int:pk>/', manager_box_views.box_delete_view, name='box_delete'),
    path('box/manager/box-types/', manager_box_views.box_type_list_view, name='box_type_list'),
    path('box/manager/box-type/create/', manager_box_views.box_type_create_view, name='box_type_create'),
    path('box/manager/box-type/edit/<int:pk>/', manager_box_views.box_type_edit_view, name='box_type_edit'),
    path('box/manager/box-type/delete/<int:pk>/', manager_box_views.box_type_delete_view, name='box_type_delete'),
    path('box/manager/items/', manager_box_views.item_list_view, name='item_list'),
    path('box/manager/item/create/', manager_box_views.item_create_view, name='item_create'),
    path('box/manager/item/edit/<int:pk>/', manager_box_views.item_edit_view, name='item_edit'),
    path('box/manager/item/delete/<int:pk>/', manager_box_views.item_delete_view, name='item_delete'),

    path("economy-game/", economy_game_view.economy_game, name="economy-game"),
    path("economy-game/fight/<int:monster_id>/", economy_game_view.fight_monster, name="fight-monster"),
    path("economy-game/enchant/", economy_game_view.enchant_weapon, name="enchant-weapon"),
    path("economy-game/monster/<int:monster_id>/is_alive/", economy_game_view.is_monster_alive, name="monster-is-alive"),

    path('battle-pass/', battle_pass.battle_pass_view, name='battle_pass'),
    path('battle-pass/claim/<int:reward_id>/', battle_pass.claim_reward, name='claim_reward'),
    path('battle-pass/buy-premium/', battle_pass.buy_battle_pass_premium_view, name='buy_battle_pass_premium'),
    path('battle-pass/exchange/', battle_pass.exchange_items_view, name='exchange_items'),
    path('battle-pass/exchange/<int:exchange_id>/', battle_pass.exchange_item, name='exchange_item'),
]
