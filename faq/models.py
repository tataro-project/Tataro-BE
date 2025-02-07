from django.db import models

from helpers.models import BaseModel
from user.models import User


class FAQ(BaseModel):
    question = models.TextField()
    answer = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="faqs")
