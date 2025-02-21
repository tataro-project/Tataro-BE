from django.db import models
from django.utils.timezone import now

from order.models import Order
from user.models import User


class Payment(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "결제 대기"
        PAID = "paid", "결제 완료"
        CANCELED = "canceled", "주문 취소"
        FAILED = "failed", "결제 실패"
        REFUNDED = "refunded", "환불 완료"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")  # 결제한 사용자
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")  # 주문 정보
    imp_uid = models.CharField(max_length=100, unique=True, null=True, blank=True)  # 포트원 결제 고유번호
    merchant_uid = models.CharField(max_length=100, unique=True)  # 가맹점 주문번호 (order_id와 동일하게 사용)
    payment_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 결제 금액
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)  # 결제 상태
    pg_provider = models.CharField(max_length=50, blank=True, null=True)  # PG사 (예: "nice", "kcp")
    pay_method = models.CharField(max_length=50, blank=True, null=True)  # 결제 방법 (예: "card", "bank_transfer")
    receipt_url = models.URLField(blank=True, null=True)  # 영수증 URL (포트원에서 제공)
    transaction_time = models.DateTimeField(auto_now_add=True)  # 결제 시각
    updated_at = models.DateTimeField(auto_now=True)  # 결제 내역 업데이트 시각

    def __str__(self) -> str:
        return f"결제 {self.merchant_uid} - {self.status}"


class Refund(models.Model):
    class StatusChoices(models.TextChoices):
        REQUESTED = "requested", "환불 요청"
        PROCESSING = "processing", "환불 처리 중"
        COMPLETED = "completed", "환불 완료"
        FAILED = "failed", "환불 실패"

    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name="refund")  # 1:1 관계
    refund_amount = models.PositiveIntegerField()  # 환불 금액
    reason = models.TextField(blank=True, null=True)  # 환불 사유
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.REQUESTED)
    requested_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)  # 환불 완료 시간

    def mark_as_completed(self):  # type: ignore
        """환불 완료 상태로 변경"""
        self.status = self.StatusChoices.COMPLETED
        self.completed_at = now()
        self.save()
