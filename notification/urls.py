from django.urls import path
from content.consumers import NotificationConsumer

urlpatterns = [
    path("ws/notifications/", NotificationConsumer.as_asgi()),
]
