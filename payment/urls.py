from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("request/", views.payment_request, name="payment_request"),
    # path("response/", views.PaymentResponseView.as_view(), name="payment_response"),
]
