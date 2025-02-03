from typing import Any, Dict
from rest_framework import serializers
from .models import TaroChatRooms, TaroCardContents, TaroChatContents

class TaroChatContentsInitSerializer(serializers.ModelSerializer[TaroChatContents]):
    class Meta:
        # User 모델과 매핑
        model = TaroChatContents
        # 시리얼라이저에 포함할 필드들을 지정
        fields = ["content", "created_at", "updated_at"]
        read_only_fields = ("created_at", "updated_at")

    def create(self, validated_data):
        # 새로운 TaroChatRooms 객체 생성
        user = self.context['request'].user  # 현재 요청의 사용자 가져오기
        room = TaroChatRooms.objects.create(user=user)

        # TaroChatContents 객체 생성 및 저장
        chat_content = TaroChatContents.objects.create(room=room, **validated_data)
        return chat_content


class TaroChatLogSerializer(serializers.Serializer):
    question = serializers.CharField()
    content = serializers.ListField(
        child=serializers.CharField()
    )
    card_name = serializers.CharField()
    card_url = serializers.URLField()
    card_content = serializers.CharField()

class TaroChatRoomResponseSerializer(serializers.Serializer):
    room_id = serializers.IntegerField()
    chat_log = TaroChatLogSerializer(many=True)