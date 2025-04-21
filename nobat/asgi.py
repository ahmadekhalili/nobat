import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# ← import your app’s websocket URL patterns
from main.routing import websocket_urlpatterns

# ← make sure this matches your project’s settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nobat.settings")

# Instantiate the standard Django ASGI application for HTTP
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # HTTP → Django views
    "http": django_asgi_app,

    # WebSocket → Channels consumers
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
