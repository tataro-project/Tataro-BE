from typing import Any, Dict

from rest_framework import serializers

from ..models import Questionnaire


# Questionnaire 모델의 데이터를 JSON 형식으로 변환하거나
# JSON 데이터를 Questionnaire 모델로 변환하는 시리얼라이저
class QuestionnaireSerializer(serializers.ModelSerializer[Questionnaire]):
    class Meta:
        # Questionnaire 모델과 매핑
        model = Questionnaire
        # 모든 필드를 시리얼라이저에 포함
        fields = "__all__"
        # user 필드는 읽기 전용으로 설정하여 수정 불가능
        read_only_fields = ["user"]

    # 문진표 데이터 수정을 처리하는 메서드
    def update(self, instance: Questionnaire, validated_data: Dict[str, Any]) -> Questionnaire:
        # validated_data: 유효성 검사가 완료된 수정할 데이터
        # instance: 수정할 Questionnaire 객체

        # validated_data의 각 필드와 값을 순회
        for attr, value in validated_data.items():
            # setattr: 객체의 속성을 동적으로 설정하는 파이썬 내장 함수
            # instance의 각 필드(attr)를 새로운 값(value)으로 업데이트
            setattr(instance, attr, value)

        # 변경된 데이터를 데이터베이스에 저장
        instance.save()

        # 수정된 문진표 객체 반환
        return instance
