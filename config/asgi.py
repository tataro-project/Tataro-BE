"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.core.wsgi import get_wsgi_application
from django.urls import path

from content.consumers import NotificationConsumer

environment = os.getenv("DJANGO_ENV", "dev")  # 기본값은 dev
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"config.settings.{environment}")

wsgi_application = get_wsgi_application()

# ASGI 애플리케이션 (웹소켓)
application = ProtocolTypeRouter(
    {
        "http": wsgi_application,  # 일반 HTTP 요청은 WSGI로 처리
        "websocket": URLRouter(
            [
                path("ws/notifications/", NotificationConsumer.as_asgi()),
            ]
        ),
    }
)
