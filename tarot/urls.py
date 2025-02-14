from django.urls import path

from tarot.views import TarotAfterInitViewSet, TarotGenerateViewSet, TarotInitViewSet

urlpatterns = [
    path("init/", TarotInitViewSet.as_view({"post": "init_create"}), name="tarot-init"),
    path("init/<int:room_id>/", TarotAfterInitViewSet.as_view({"post": "after_create"}), name="tarot-init-after"),
    path("<int:pk>/", TarotGenerateViewSet.as_view({"post": "create"}), name="tarot_generate"),
]
