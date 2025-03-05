from django.contrib.postgres.fields import ArrayField
from django.db import models

from helpers.models import BaseModel, Category
from user.models import User


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()  # content 를 title에 연결할 link 주소로 사용함.
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    category = models.CharField(max_length=20)


class NotiUser(BaseModel):
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="notiusers")
    read_users = ArrayField(models.IntegerField(), default=list, blank=True)  # 수정: 기존 'notiusers'에서 변경
