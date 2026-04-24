import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack   # ✅ ADD THIS
import Client_panel.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StayEase.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(   # ✅ WRAP WITH THIS
        URLRouter(
            Client_panel.routing.websocket_urlpatterns
        )
    ),
})