from django.urls import path

from .views import PaymentWebhookView, VerifyPaymentView, CreatePaymentView, payment_page

urlpatterns = [
    # payment api url
    path("create/", CreatePaymentView.as_view(), name="create_payment"),
    path("verify/", VerifyPaymentView.as_view(), name="verify_payment"),
    path("webhook/", PaymentWebhookView.as_view(), name="payment_webhook"),
    path("payment/", payment_page, name="payment_page"),

]