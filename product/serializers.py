from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = Product
        fields = "__all__"  # 모든 필드를 포함
