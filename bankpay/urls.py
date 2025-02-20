from django.urls import path

from .views import BankTransferView

urlpatterns = [
    path("bank/", BankTransferView.as_view(), name="payment_request"),
]
