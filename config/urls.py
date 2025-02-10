"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.urls.conf import re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from notification.consumers import NotificationConsumer

schema_view = get_schema_view(
    openapi.Info(
        title="리뷰 API",
        default_version="v1",
        description="리뷰 관리를 위한 API",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # 기존 URL 패턴들...
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    path("admin/", admin.site.urls),
    # path("api/v1/", include("tarot.urls")),
    # content path
    path("api/v1/review/", include("review.urls")),
    path("api/v1/notice/", include("notice.urls")),
    path("api/v1/faq/", include("faq.urls")),
    # product path
    path("api/v1/product/", include("product.urls")),  # product 앱 추가
    # notification path
    path("ws/notifications/", NotificationConsumer.as_asgi()),
    # path("api/v1/", include("user.urls")),
]
