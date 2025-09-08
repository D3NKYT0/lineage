from django.urls import path
from .views import payments_views
from .views import mercadopago_views
from .views import stripe_views


app_name = "payment"


urlpatterns = [
    path('new/', payments_views.criar_ou_reaproveitar_pedido, name='novo_pedido'),
    path('calcular-bonus/', payments_views.calcular_bonus_ajax, name='calcular_bonus_ajax'),
    path('order/<int:pedido_id>/', payments_views.detalhes_pedido, name='detalhes_pedido'),
    path('order/<int:pedido_id>/confirm/', payments_views.confirmar_pagamento, name='confirmar_pagamento'),
    path('pending/', payments_views.pedidos_pendentes, name='pedidos_pendentes'),
    path('cancel-order/<int:pedido_id>/', payments_views.cancelar_pedido, name='cancelar_pedido'),

    # Mercado Pago
    path('mercadopago/sucesso/', mercadopago_views.pagamento_sucesso, name='pagamento_sucesso'),
    path('mercadopago/erro/', mercadopago_views.pagamento_erro, name='pagamento_erro'),
    path('mercadopago/notificacao/', mercadopago_views.notificacao_mercado_pago, name='notificacao_mercado_pago'),

    # Stripe
    path('stripe/sucesso/', stripe_views.stripe_pagamento_sucesso, name='stripe_pagamento_sucesso'),
    path('stripe/erro/', stripe_views.stripe_pagamento_erro, name='stripe_pagamento_erro'),
    path('stripe/webhook/', stripe_views.stripe_webhook, name='stripe_webhook'),
]
