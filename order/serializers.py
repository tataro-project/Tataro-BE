from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer[Order]):
    class Meta:
        model = Order
        fields = ["id", "user", "product", "count", "order_id", "total_amount", "status"]
        read_only_fields = ["user", "order_id", "status"]
