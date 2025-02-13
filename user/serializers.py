from typing import Any, Dict

from rest_framework import serializers

from .models import User


# User 모델의 데이터를 JSON 형식으로 변환하거나
# JSON 데이터를 User 모델로 변환하는 시리얼라이저
class UserUpdateSerializer(serializers.ModelSerializer[User]):
    birthday = serializers.DateTimeField(source="birth")

    class Meta:
        # User 모델과 매핑
        model = User
        # 시리얼라이저에 포함할 필드들을 지정
        fields = ["id", "nickname", "email", "gender", "birthday", "social_type"]
        # 수정 불가능한 필드들 지정 (읽기 전용)
        read_only_fields = ["id", "email", "social_type"]

    # 사용자 정보 수정을 처리하는 메서드
    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        # validated_data: 유효성 검사가 완료된 수정할 데이터
        # instance: 수정할 User 객체

        # get 메서드를 사용하여 새로운 값이 있으면 업데이트, 없으면 기존 값 유지
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.gender = validated_data.get("gender", instance.gender)
        instance.birth = validated_data.get("birthday", instance.birth)

        # 변경된 데이터를 데이터베이스에 저장
        instance.save()

        # 수정된 사용자 객체 반환
        return instance
