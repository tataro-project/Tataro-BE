from models import Review
from rest_framework import serializers


class ReviewSerializer(serializers.ModelSerializer[Review]):
    user = serializers.ReadOnlyField(source="user.id")  # 유저 아이디를 반환

    class Meta:
        model = Review
        fields = "__all__"
