from django.db import models

from user.models import User


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class TaroChatRooms(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class TaroCardContents(TimeStampedModel):
    room = models.ForeignKey(TaroChatRooms, on_delete=models.CASCADE)
    card_id = models.IntegerField()
    card_content = models.TextField()

class TaroChatContents(TimeStampedModel):
    room = models.ForeignKey(TaroChatRooms, on_delete=models.CASCADE)
    content = models.TextField()
