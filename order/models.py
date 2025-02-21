from django.db import models

from helpers.models import BaseModel
from product.models import Product
from user.models import User


class Order(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "결제 대기"
        PAID = "paid", "결제 완료"
        CANCELED = "canceled", "주문 취소"
        FAILED = "failed", "결제 실패"
        REFUNDED = "refunded", "환불 완료"

    # 기본 주문 정보
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")  # 주문한 사용자
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    count = models.IntegerField(default=1)
    order_id = models.CharField(max_length=100, unique=True)  # 주문 번호 (고유값)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 총 결제 금액
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)  # 주문 상태
    product_name = models.CharField(max_length=100, default="")

    def __str__(self) -> str:
        return f"주문 {self.order_id} - {self.user.username} ({self.status})"
