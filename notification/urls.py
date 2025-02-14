from django.urls import path

from notification.views import create_notification

urlpatterns = [
    path("", create_notification, name="notification-create"),
]
