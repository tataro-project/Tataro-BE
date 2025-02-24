from django.urls import path

from notification import views
from notification.views import create_notification

urlpatterns = [
    path("", create_notification, name="notification-create"),
    path("mark-as-read/", views.mark_notification_as_read, name="mark_notification_as_read"),
]
