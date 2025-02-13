from rest_framework import serializers

from .models import Category, Notice


class CategorySerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class NoticeSerializer(serializers.ModelSerializer):  # type: ignore
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), allow_null=True)

    class Meta:
        model = Notice
        fields = ["id", "title", "content", "img_url", "order", "user", "category"]

    def to_representation(self, instance):  # type: ignore
        representation = super().to_representation(instance)
        representation["category"] = CategorySerializer(instance.category).data if instance.category else None
        return representation
