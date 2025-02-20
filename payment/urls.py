from django.urls import path

from .views import PaymentWebhookView, VerifyPaymentView

urlpatterns = [
    path("verify/", VerifyPaymentView.as_view(), name="verify_payment"),
    path("webhook/", PaymentWebhookView.as_view(), name="payment_webhook"),
]
