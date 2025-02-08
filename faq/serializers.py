from rest_framework import serializers

from .models import FAQ


class FAQSerializer(serializers.ModelSerializer[FAQ]):
    user = serializers.ReadOnlyField(source="user.id")  # 작성자 표시

    class Meta:
        model = FAQ
        fields = "__all__"
