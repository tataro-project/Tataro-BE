from rest_framework import serializers

from .models import FAQ, Notice, Review


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
