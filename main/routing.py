from django.urls import re_path
from .consumers import BrowserStatusConsumer

# // URLهای WebSocket رو اینجا تعریف می‌کنیم
websocket_urlpatterns = [
    re_path(r"ws/status/$", BrowserStatusConsumer.as_asgi()),  # // ws://…/ws/status/
]
