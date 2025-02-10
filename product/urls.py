from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProductViewSet

router = DefaultRouter()
router.register(r"", ProductViewSet)  # /api/v1/product/ 엔드포인트

urlpatterns = [
    path("", include(router.urls)),  # product 관련 API 등록
]
