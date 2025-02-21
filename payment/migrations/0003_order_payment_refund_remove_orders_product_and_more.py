# Generated by Django 5.1.6 on 2025-02-21 15:45

import datetime

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0002_portone_rename_order_orders_and_more"),
        ("product", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="생성일")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="수정일")),
                ("count", models.IntegerField(default=1)),
                ("order_id", models.CharField(max_length=100, unique=True)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "결제 대기"),
                            ("paid", "결제 완료"),
                            ("canceled", "주문 취소"),
                            ("failed", "결제 실패"),
                            ("refunded", "환불 완료"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="product.product")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="orders", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("imp_uid", models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ("merchant_uid", models.CharField(max_length=100, unique=True)),
                ("payment_id", models.CharField(blank=True, max_length=100, null=True, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "결제 대기"),
                            ("paid", "결제 완료"),
                            ("canceled", "주문 취소"),
                            ("failed", "결제 실패"),
                            ("refunded", "환불 완료"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("pg_provider", models.CharField(blank=True, max_length=50, null=True)),
                ("pay_method", models.CharField(blank=True, max_length=50, null=True)),
                ("receipt_url", models.URLField(blank=True, null=True)),
                ("transaction_time", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="payment.order"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Refund",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("refund_amount", models.PositiveIntegerField()),
                ("reason", models.TextField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("requested", "환불 요청"),
                            ("processing", "환불 처리 중"),
                            ("completed", "환불 완료"),
                            ("failed", "환불 실패"),
                        ],
                        default="requested",
                        max_length=20,
                    ),
                ),
                ("requested_at", models.DateTimeField(default=datetime.datetime(2025, 2, 21, 15, 45, 58, 454231))),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "payment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, related_name="refund", to="payment.payment"
                    ),
                ),
            ],
        ),
        migrations.RemoveField(
            model_name="orders",
            name="product",
        ),
        migrations.RemoveField(
            model_name="orders",
            name="user",
        ),
        migrations.RemoveField(
            model_name="payments",
            name="order",
        ),
        migrations.RemoveField(
            model_name="payments",
            name="bank_transfer",
        ),
        migrations.RemoveField(
            model_name="payments",
            name="user",
        ),
        migrations.DeleteModel(
            name="Portone",
        ),
        migrations.DeleteModel(
            name="Orders",
        ),
        migrations.DeleteModel(
            name="Payments",
        ),
    ]
