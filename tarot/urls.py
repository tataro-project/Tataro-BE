from django.urls import path

from tarot.views import TarotGenerateViewSet, TarotInitViewSet

urlpatterns = [
    path("init/", TarotInitViewSet.as_view({"post": "init"}), name="tarot-init"),
    path("<int:pk>/", TarotGenerateViewSet.as_view({"post": "create"}), name="tarot_generate"),
]
