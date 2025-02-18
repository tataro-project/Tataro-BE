"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

environment = os.getenv("DJANGO_ENV", "dev")  # 기본값은 dev
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{environment}")

django.setup()

from helpers.custom_middleware import TokenAuthMiddleware
from notification.routing import websocket_urlpatterns

# ASGI 애플리케이션 (웹소켓)
application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),  # 기존 WSGI 기반 앱 유지
        "websocket": TokenAuthMiddleware(URLRouter(websocket_urlpatterns)),  # type: ignore # 웹소켓은 ASGI 사용
    }
)
