from django.db import models

from user.models import User


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TaroChatRooms(TimeStampedModel):
    card_id = models.IntegerField()
    card_content = models.TextField()
    category = models.ForeignKey(User, on_delete=models.CASCADE)
