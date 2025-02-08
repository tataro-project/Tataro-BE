from django.db import models

from helpers.models import BaseModel
from user.models import User


class Notice(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.URLField(max_length=500, blank=True, null=True)  # URLField로 변경
    order = models.IntegerField(blank=True, null=True, default=None)  # None 허용
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notices")

    def __str__(self) -> str:
        return self.title
