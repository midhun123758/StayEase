import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import Client_panel.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "StayEase.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        Client_panel.routing.websocket_urlpatterns
    ),
})