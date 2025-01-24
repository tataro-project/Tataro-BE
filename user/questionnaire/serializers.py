from typing import Any
from rest_framework import serializers
from ..models import Questionnaire

class QuestionnaireSerializer(serializers.ModelSerializer[Questionnaire]):
    class Meta:
        model = Questionnaire
        fields = '__all__'
