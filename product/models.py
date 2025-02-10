from django.db import models

from helpers.models import BaseModel


class Product(BaseModel):
    # 기본 필드
    id = models.AutoField(
        primary_key=True
    )  # 자동 증가 ID (기본적으로 Django는 pk를 자동 생성하지만 명시적으로 추가 가능)
    name = models.CharField(max_length=255)  # 제품 이름
    description = models.TextField(blank=True, null=True)  # 제품 설명 (빈 값 허용)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 제품 가격
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # 할인 가격 (옵션)
    img_url = models.URLField(max_length=500, blank=True, null=True)  # 이미지 URL (옵션)

    # 생성 및 수정 시간 기록
    created_at = models.DateTimeField(auto_now_add=True)  # 생성 시간 (자동 기록)
    updated_at = models.DateTimeField(auto_now=True)  # 수정 시간 (자동 갱신)

    # 활성화 여부
    is_active = models.BooleanField(default=True)  # 활성화 상태 (기본값: 활성화)

    def __str__(self) -> str:
        return self.name  # 객체를 문자열로 표현할 때 이름 반환
