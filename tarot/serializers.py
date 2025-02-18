from typing import Any, Dict

from rest_framework import serializers

from .models import TaroCardContents, TaroChatContents, TaroChatRooms


class TaroChatContentsInitSerializer(serializers.ModelSerializer[TaroChatContents]):
    # 직접 외부에서 데이터를 입력
    chat_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        # User 모델과 매핑
        model = TaroChatContents
        # 시리얼라이저에 포함할 필드들을 지정
        fields = ["chat_id", "content", "room_id", "created_at", "updated_at"]
        read_only_fields = ("created_at", "updated_at", "room_id")

    def create(self, validated_data: dict[str, Any]) -> TaroChatContents:
        room_id = self.context.get("room_id")
        # 새로운 TaroChatRooms 객체 생성
        if not room_id:
            room_id = TaroChatRooms.objects.create(user=self.context["request"].user).id  # 테스트 후 user로 변경

        # TaroChatContents 객체 생성 및 저장
        chat_content = TaroChatContents.objects.create(room_id=room_id, **validated_data)
        return chat_content

    # SerializerMethodField에 값 입력
    def get_chat_id(self, obj: TaroChatContents) -> Any | None:
        return self.context.get("chat_id")


class TaroChatLogSerializer(serializers.Serializer["TaroCardContents"]):
    question = serializers.CharField()
    content = serializers.CharField()
    card_name = serializers.CharField()
    card_url = serializers.URLField()
    card_content = serializers.CharField()
    card_direction = serializers.CharField()


class TaroChatRoomResponseSerializer(serializers.Serializer["TaroChatLogSerializer"]):
    room_id = serializers.IntegerField()
    chat_log = TaroChatLogSerializer(many=True)


class TaroChatAllRoomResponseSerializer(serializers.Serializer["TaroChatRoomResponseSerializer"]):
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    total_count = serializers.IntegerField()
    total_pages = serializers.IntegerField()
    chat_contents = TaroChatRoomResponseSerializer(many=True)
