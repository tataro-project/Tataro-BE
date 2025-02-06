from django.db import models

from helpers.models import BaseModel
from user.models import User


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")


class NotiUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notiusers")
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="notiusers")
    is_read = models.BooleanField(default=False)
