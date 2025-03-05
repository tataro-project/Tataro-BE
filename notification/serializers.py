from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer[Notification]):
    class Meta:
        model = Notification
        fields = ["id", "title", "content", "user", "created_at", "updated_at", "category"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    # 자동으로 생성된다고 함
    # def create(self, validated_data) -> Notification:  # type: ignore
    #     """알림 생성 시 자동으로 사용자 정보를 추가"""
    #     request = self.context.get("request")
    #     if request and request.user.is_authenticated:
    #         validated_data["user"] = request.user
    #     return super().create(validated_data)
