from rest_framework import serializers

from .models import Order


class OrderSerializer(serializers.ModelSerializer[Order]):
    class Meta:
        model = Order
        fields = ["id", "user", "product", "count", "order_id", "total_amount", "status", "product_name"]
        read_only_fields = ["user", "order_id", "status", "product_name"]

    def create(self, validated_data):
        # 상품명 추출
        product = validated_data['product']
        validated_data['product_name'] = product.name
        return super().create(validated_data)

    total_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        coerce_to_string=False  # 숫자 타입 유지
    )