from rest_framework import serializers

from .models import FAQ, Notice, Notification, Review


class ReviewSerializer(serializers.ModelSerializer[Review]):
    user = serializers.ReadOnlyField(source="user.id")  # 유저 아이디를 반환

    class Meta:
        model = Review
        fields = "__all__"


class NoticeSerializer(serializers.ModelSerializer[Notice]):
    user = serializers.ReadOnlyField(source="user.id")  # 작성자 표시

    class Meta:
        model = Notice
        fields = "__all__"


class FAQSerializer(serializers.ModelSerializer[FAQ]):
    user = serializers.ReadOnlyField(source="user.id")  # 작성자 표시

    class Meta:
        model = FAQ
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer[Notification]):
    class Meta:
        model = Notification
        fields = ["id", "title", "content", "img_url", "user", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]

    def create(self, validated_data) -> Notification:  # type: ignore
        """알림 생성 시 자동으로 사용자 정보를 추가"""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["user"] = request.user
        return super().create(validated_data)
