from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet

router = DefaultRouter()
router.register("", OrderViewSet)  # 'orders/' 엔드포인트 생성

urlpatterns = [
    path("", include(router.urls)),
]
