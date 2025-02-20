from django.db import models
from django.utils.translation import gettext_lazy as _

from bankpay.models import BankTransfer
from helpers.models import BaseModel
from product.models import Product
from user.models import User


class Portone(BaseModel):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", _("결제 대기")
        PAID = "paid", _("결제 완료")
        FAILED = "failed", _("결제 실패")
        CANCELLED = "cancelled", _("결제 취소")
        REFUNDED = "refunded", _("환불 완료")

    imp_uid = models.CharField(max_length=50, unique=True, verbose_name="포트원 결제 고유번호")
    merchant_uid = models.CharField(max_length=50, unique=True, verbose_name="가맹점 주문번호")
    amount = models.PositiveIntegerField(verbose_name="결제 금액")
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING, verbose_name="결제 상태"
    )
    buyer_email = models.EmailField(verbose_name="구매자 이메일", null=True, blank=True)
    buyer_name = models.CharField(max_length=100, verbose_name="구매자 이름", null=True, blank=True)
    buyer_tel = models.CharField(max_length=20, verbose_name="구매자 전화번호", null=True, blank=True)

    def __str__(self):  # type: ignore
        return f"{self.merchant_uid} - {self.status}"


class Orders(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)


class Payments(BaseModel):
    # bank_transfer: 무통장결제, "" pending: 결제 진행중, complete: 결제 완료, failed: 결제 실패
    METHOD_CHOICES = (("bank_transfer", "bank_transfer"), ("port_one", "port_one"))
    STATUS_CHOICES = (("pending", "pending"), ("complete", "complete"), ("failed", "failed"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_transfer = models.ForeignKey(BankTransfer, on_delete=models.CASCADE)
    order = models.ForeignKey(Orders, on_delete=models.CASCADE)
    amount = models.IntegerField()
    method = models.CharField(choices=METHOD_CHOICES)
    status = models.CharField(choices=STATUS_CHOICES)
