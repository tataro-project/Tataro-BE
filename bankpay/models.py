from django.db import models

from helpers.models import BaseModel


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
    deadline = models.DateField()
    status = models.CharField(choices=STATUS_CHOICES)
