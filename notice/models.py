from django.db import models

from helpers.models import BaseModel
from user.models import User


class Notice(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.URLField(max_length=500, blank=True, null=True)
    order = models.IntegerField(blank=True, null=True, default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notices")
    category = models.CharField(max_length=20)

    def __str__(self) -> str:
        return self.title
