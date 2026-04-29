import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StayEase.settings")
django.setup()

# Initialize the ASGI application early
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Client_panel.routing 

application = ProtocolTypeRouter({
    "http": django_asgi_app, # 
    "websocket": AuthMiddlewareStack(
        URLRouter(
            Client_panel.routing.websocket_urlpatterns
        )
    ),
})