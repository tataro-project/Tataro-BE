from datetime import timedelta

from django.core.cache import cache
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import no_body, swagger_auto_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from bankpay.models import BankOrders, BankPayments, BankTransfer
from bankpay.serializer import (
    AdminAccountSerializer,
    BankTransferGetListSerializer,
    BankTransferGetResponseSerializer,
    BankTransferRequestSerializer,
)
from product.models import Product

PAYMENT_DEADLINE_HOURS = 24
ADMIN_NAME = "홍길동"
ADMIN_ACCOUNT = "000000-0000000-0000000"
ADMIN_BANK = "농협은행"


class BankTransferView(APIView):
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
            order = BankOrders.objects.create(product=product, user=request.user)
            bank_transfer = BankTransfer.objects.create(  # type:ignore
                name=req_serial.data.get("name"),
                deadline=timezone.now() + timedelta(hours=PAYMENT_DEADLINE_HOURS),
                status="pending",
            )
            payments = BankPayments.objects.create(
                user=request.user,
                bank_transfer=bank_transfer,
                order=order,
                amount=int(product.price * order.count),
                method="bank_transfer",
                status="pending",
            )
            # 내역 새로 생성될때 캐쉬 업데이트
            total_count = BankPayments.objects.filter(user=request.user).count()
            cache.set(f"pay_log_count_{request.user.id}", total_count)

            data = {
                "admin_account": ADMIN_ACCOUNT,
                "admin_name": ADMIN_NAME,
                "admin_bank": ADMIN_BANK,
                "deadline": bank_transfer.deadline,
                "depositor_name": payments.bank_transfer.name,
                "deposit_amount": payments.amount,
                "heart_count": int("".join([i for i in payments.order.product.name if i.isdigit()])),
                "payments_id": payments.id,
            }
            res_serializer = AdminAccountSerializer(data=data)
            res_serializer.is_valid(raise_exception=True)
            return Response(res_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(  # type:ignore
        operation_summary="결제 로그 페이지네이션",
        operation_description="모든 결제 로그를 페이지네이션을 통해 원하는 페이지의 로그 내역을 응답합니다.",
        manual_parameters=[
            openapi.Parameter(
                "page", openapi.IN_QUERY, description="페이지 번호", type=openapi.TYPE_INTEGER, required=True
            ),
            openapi.Parameter(
                "size", openapi.IN_QUERY, description="페이지 당 게시글 개수", type=openapi.TYPE_INTEGER, required=True
            ),
        ],
        request_body=no_body,
        responses={200: BankTransferGetListSerializer},
    )
    def get(self, request):
        page = int(self.request.query_params.get("page", 1))
        size = int(self.request.query_params.get("size", 1))
        queryset = (
            BankPayments.objects.prefetch_related("bank_transfer")
            .prefetch_related("order__product")
            .filter(user=request.user)
            .order_by("-created_at")
        )

        # 캐시 키 생성
        cache_key = f"pay_log_count_{request.user.id}"
        # 캐시된 count 확인
        total_count = cache.get(cache_key)
        if total_count is None:
            total_count = queryset.count()
            # count 결과를 캐시에 5분간 저장
            cache.set(cache_key, total_count)

        start = (page - 1) * size
        end = min(start + size, total_count)
        paginated_queryset = queryset[start:end]

        result_list = []
        for bank_log in paginated_queryset:
            data = {
                "product_id": bank_log.order.product.id,
                "payments_id": bank_log.id,
                "purchase_date": bank_log.created_at,
                "payment_amount": bank_log.amount,
                "payment_status": bank_log.bank_transfer.status,
            }
            serializer = BankTransferGetResponseSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            result_list.append(serializer.data)
        response_serializer = BankTransferGetListSerializer(
            data={
                "payment_details": result_list,
                "page": page,
                "size": size,
                "total_count": total_count,
                "total_pages": (total_count + size - 1) // size,
            }
        )
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class BankTransferIdView(APIView):
    @swagger_auto_schema(  # type:ignore
        operation_summary="무통장 결제 상세정보",
        operation_description="관리자 계좌 정보와 입금 기한을 응답합니다.",
        request_body=no_body,
        responses={201: AdminAccountSerializer},
    )
    def get(self, request, payment_id):
        query = (
            BankPayments.objects.prefetch_related("bank_transfer")
            .prefetch_related("order__product")
            .filter(user=request.user, pk=payment_id)
        )
        bank_payments = get_object_or_404(query)
        data = {
            "admin_account": ADMIN_ACCOUNT,
            "admin_name": ADMIN_NAME,
            "admin_bank": ADMIN_BANK,
            "deadline": bank_payments.bank_transfer.deadline,
            "depositor_name": bank_payments.bank_transfer.name,
            "deposit_amount": bank_payments.amount,
            "heart_count": int("".join([i for i in bank_payments.order.product.name if i.isdigit()])),
            "payments_id": payment_id,
        }
        res_serializer = AdminAccountSerializer(data=data)
        res_serializer.is_valid(raise_exception=True)
        return Response(res_serializer.data, status=status.HTTP_201_CREATED)
