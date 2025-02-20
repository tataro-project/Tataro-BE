from django.urls import path

from .views import BankTransferView

urlpatterns = [
    path("", BankTransferView.as_view(), name="payment_request"),
]
