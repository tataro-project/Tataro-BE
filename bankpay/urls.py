from django.urls import path

from .views import BankTransferIdView, BankTransferView

urlpatterns = [
    path("", BankTransferView.as_view(), name="payment_request"),
    path("<int:payment_id>/addinform/", BankTransferIdView.as_view(), name="payment_id_log"),
]
