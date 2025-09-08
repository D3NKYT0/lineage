"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Configurar Django antes de importar os apps
import django
django.setup()

def get_websocket_urlpatterns():
    """Carrega as rotas WebSocket de forma segura"""
    patterns = []
    
    # Tenta importar as rotas do administrator
    try:
        from apps.main.administrator.routing import websocket_urlpatterns as admin_ws
        patterns.extend(admin_ws)
    except ImportError:
        pass
    
    # Tenta importar as rotas de notificação
    try:
        from apps.main.notification.routing import websocket_urlpatterns as notif_ws
        patterns.extend(notif_ws)
    except ImportError:
        pass
    
    # Tenta importar as rotas de mensagem
    try:
        from apps.main.message.routing import websocket_urlpatterns as message_ws
        patterns.extend(message_ws)
    except ImportError:
        pass
    
    return patterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(get_websocket_urlpatterns())
    ),
})
