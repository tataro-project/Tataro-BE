from random import choices

from django.utils import timezone
from rest_framework import serializers

from bankpay.models import BankTransfer


class BankTransferRequestSerializer(serializers.Serializer):  # type:ignore
    product_id = serializers.IntegerField()
    name = serializers.CharField()


class AdminAccountSerializer(serializers.Serializer):  # type:ignore
    admin_account = serializers.CharField(help_text="관리자 계좌번호", max_length=30)
    payments_id = serializers.IntegerField()


class BankTransferGetResponseSerializer(serializers.Serializer):  # type:ignore
    payments_id = serializers.IntegerField()
    purchase_date = serializers.DateTimeField(default_timezone=timezone.get_default_timezone())
    quantity = serializers.IntegerField(default=1)
    payment_amount = serializers.IntegerField()
    payment_method = serializers.CharField(default="bank_transfer")
    payment_status = serializers.ChoiceField(choices=BankTransfer.STATUS_CHOICES)


class BankTransferGetListSerializer(serializers.Serializer):  # type:ignore
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    total_count = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    payment_details = BankTransferGetResponseSerializer(many=True)
