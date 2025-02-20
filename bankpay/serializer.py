from rest_framework import serializers


class BankTransferRequestSerializer(serializers.Serializer):  # type:ignore
    product_id = serializers.IntegerField()
    name = serializers.CharField()


class AdminAccountSerializer(serializers.Serializer):  # type:ignore
    admin_account = serializers.CharField(help_text="관리자 계좌번호", max_length=20)
