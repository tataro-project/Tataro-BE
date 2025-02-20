from datetime import timedelta

from django.utils import timezone
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from bankpay.serializer import AdminAccountSerializer, BankTransferRequestSerializer
from payment.models import Orders, Payments
from product.models import Product


class BankTransferView(APIView):
    PAYMENT_DEADLINE_HOURS = 24
    ADMIN_ACCOUNT = "000000-0000000-0000000"

    @swagger_auto_schema(  # type:ignore
        operation_summary="무통장 결제",
        operation_description="무통장 결제를 생성합니다.",
        request_body=BankTransferRequestSerializer,
        responses={201: AdminAccountSerializer},
    )
    def post(self, request):
        req_serial = BankTransferRequestSerializer(data=request.data)
        if req_serial.is_valid(raise_exception=True):
            product = get_object_or_404(Product, id=req_serial.data.get("product_id"))
            order = Orders.objects.create(product=product, user=request.user)
            bank_transfer = BankTransfer.objects.create(  # type:ignore
                name=req_serial.data.get("name"),
                deadline=timezone.now() + timedelta(hours=self.PAYMENT_DEADLINE_HOURS),
                status="pending",
            )
            payments = Payments.objects.create(
                user=request.user,
                bank_transfer=bank_transfer,
                order=order,
                amount=int(product.price * order.count),
                method="bank_transfer",
                status="pending",
            )
            data = {"admin_account": self.ADMIN_ACCOUNT, "payments_id": payments.id}
            res_serializer = AdminAccountSerializer(data=data)
            res_serializer.is_valid()
            return Response(res_serializer.data, status=status.HTTP_201_CREATED)
