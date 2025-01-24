from typing import Any, Dict
from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ['id', 'nickname', 'email', 'gender', 'birth', 'social_type']
        read_only_fields = ['id', 'email', 'social_type']

    def update(self, instance: User, validated_data: Dict[str, Any]) -> User:
        instance.nickname = validated_data.get('nickname', instance.nickname)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.birth = validated_data.get('birth', instance.birth)
        instance.save()
        return instance
