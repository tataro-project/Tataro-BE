from django.db import models

from helpers.models import BaseModel
from user.models import User


class Payment(models.Model):
    merchant_id = models.CharField(max_length=255)
    goods_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    buyer_name = models.CharField(max_length=255)
    buyer_tel = models.CharField(max_length=20)
    buyer_email = models.EmailField()
    moid = models.CharField(max_length=255)
    return_url = models.URLField()
    edi_date = models.CharField(max_length=20, blank=True, null=True)
    hash_str = models.CharField(max_length=255, blank=True, null=True)
    result_code = models.CharField(max_length=4, blank=True, null=True)
    result_msg = models.CharField(max_length=255, blank=True, null=True)
    tid = models.CharField(max_length=255, blank=True, null=True)
    app_no = models.CharField(max_length=255, blank=True, null=True)
    card_no = models.CharField(max_length=255, blank=True, null=True)
    pay_method = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Payment: {self.goods_name} - {self.price}"


class Products(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    discount_price = models.IntegerField()
    img_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)


class Order(BaseModel):
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    count = models.IntegerField(default=1)


class BankTransfer(BaseModel):
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


class Payments(BaseModel):
    METHOD_CHOICES = (("bank_transfer", "bank_transfer"), ("port_one", "port_one"))
    STATUS_CHOICES = (("pending", "pending"), ("complete", "complete"), ("failed", "failed"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bank_transfer = models.ForeignKey(BankTransfer, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.IntegerField()
    method = models.CharField(choices=METHOD_CHOICES)
    status = models.CharField(choices=STATUS_CHOICES)
