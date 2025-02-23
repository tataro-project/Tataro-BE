from django.db import models

from helpers.models import BaseModel
from product.models import Product
from user.models import User


class BankTransfer(BaseModel):
    # pending: 입금 진행중, complete: 입금 완료, canceled: 입금 취소, expired: 입금기한 만료, mismatch:입금 금액 불일치
    STATUS_CHOICES = (
        ("pending", "pending"),
        ("completed", "completed"),
        ("expired", "expired"),
        ("canceled", "canceled"),
        ("mismatch", "mismatch"),
    )
    name = models.CharField(max_length=10)
    deadline = models.DateTimeField()
    status = models.CharField(choices=STATUS_CHOICES)


class BankOrders(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)


class BankPayments(BaseModel):
    # bank_transfer: 무통장결제, "" pending: 결제 진행중, complete: 결제 완료, failed: 결제 실패
    METHOD_CHOICES = (("bank_transfer", "bank_transfer"), ("port_one", "port_one"))
    STATUS_CHOICES = (("pending", "pending"), ("complete", "complete"), ("failed", "failed"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_transfer = models.ForeignKey(BankTransfer, on_delete=models.CASCADE)
    order = models.ForeignKey(BankOrders, on_delete=models.CASCADE)
    amount = models.IntegerField()
    method = models.CharField(choices=METHOD_CHOICES)
    status = models.CharField(choices=STATUS_CHOICES)
