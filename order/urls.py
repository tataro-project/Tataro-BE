from django.urls import path

from order.views import CreatePaymentView


urlpatterns = [
    # order api url
    path("order_create", CreatePaymentView.as_view(), name="order_create"),


]