from .models import Notice
from rest_framework import serializers


class NoticeSerializer(serializers.ModelSerializer[Notice]):
    user = serializers.ReadOnlyField(source="user.id")  # 작성자 표시

    class Meta:
        model = Notice
        fields = "__all__"
