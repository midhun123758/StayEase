import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "StayEase.settings"
)

# Load Django FIRST
django_asgi_app = get_asgi_application()

# Import AFTER Django setup
import Hostlers_panel.routing
import Client_panel.routing

from Hostlers_panel.middleware import JWTAuthMiddleware


application = ProtocolTypeRouter({

    "http": django_asgi_app,

    "websocket": JWTAuthMiddleware(

        URLRouter(

            Hostlers_panel.routing.websocket_urlpatterns +

            Client_panel.routing.websocket_urlpatterns

        )
    ),
})