from rest_framework import serializers

from helpers.models import Category

from .models import Notice


class CategorySerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = Category
        fields = ["id", "name", "description"]


class NoticeSerializer(serializers.ModelSerializer):  # type: ignore

    class Meta:
        model = Notice
        fields = "__all__"


