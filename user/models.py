from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from helpers.models import BaseModel


class User(AbstractUser):
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # email을 여기서 제거

    SOCIAL_CHOICES = [("KAKAO", "Kakao"), ("NAVER", "Naver")]
    GENDER_CHOICES = [("male", "남성"), ("female", "여성")]

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=20, null=True, blank=True)  # type: ignore
    email = models.EmailField(unique=True)  # email을 unique로 설정
    nickname = models.CharField(max_length=30)
    social_type = models.CharField(max_length=10, choices=SOCIAL_CHOICES)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    birth = models.DateTimeField(null=True)
    heart_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)


class HeartUsedLog(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    heart_count = models.IntegerField()
    chat_room_id = models.IntegerField()


class Questionnaire(models.Model):
    STATUS_CHOICES = [("SINGLE", "싱글"), ("DATING", "연애중"), ("MARRIED", "기혼")]
    MARRIAGE_VALUES_CHOICES = [("POSITIVE", "긍정적"), ("NEGATIVE", "부정적"), ("NEUTRAL", "중립적")]

    id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True)
    relationship_count = models.IntegerField(null=True)
    marriage_count = models.IntegerField(null=True)
    marriage_values = models.CharField(max_length=20, choices=MARRIAGE_VALUES_CHOICES, null=True)
    job = models.CharField(max_length=20, null=True)
    gender = models.CharField(max_length=10, choices=User.GENDER_CHOICES, null=True)
    age = models.IntegerField(null=True)
    relationship_start = models.DateTimeField(null=True)
    relationship_end = models.DateTimeField(null=True)
    marriage_start = models.DateTimeField(null=True)
    marriage_end = models.DateTimeField(null=True)
    longest_relationship_period = models.DateTimeField(null=True)
    emotional_state = models.CharField(max_length=30, null=True)
    love_satisfaction = models.IntegerField(null=True)
