from rest_framework import serializers

from .models import Review


class ReviewSerializer(serializers.ModelSerializer[Review]):
    user_nickname = serializers.CharField(source="user.nickname", read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "title",
            "content",
            "img_url",
            "on_main",
            "view_count",
            "user_nickname",
            "taro_chat_room",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user_nickname"]
