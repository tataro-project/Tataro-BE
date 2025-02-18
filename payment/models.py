from django.db import models


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
