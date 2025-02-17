from django.urls import path

from tarot.views import (
    TarotAfterInitViewSet,
    TarotGenerateViewSet,
    TarotInitViewSet,
    TarotLogViewSet,
)

urlpatterns = [
    path("init/", TarotInitViewSet.as_view({"post": "init_create"}), name="tarot-init"),
    path("init/<int:room_id>/", TarotAfterInitViewSet.as_view({"post": "after_create"}), name="tarot-init-after"),
    path("<int:pk>/", TarotGenerateViewSet.as_view({"post": "create"}), name="tarot_generate"),
    path("logs/", TarotLogViewSet.as_view({"get": "get_all_log"}), name="all_log"),
    path("logs/first/", TarotLogViewSet.as_view({"get": "get_newest_log"}), name="newest_log"),
    path("logs/<int:pk>/", TarotLogViewSet.as_view({"get": "get_before_log"}), name="before_log"),
]
