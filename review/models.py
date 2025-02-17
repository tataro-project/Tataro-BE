from django.db import models

from helpers.models import BaseModel
from tarot.models import TaroChatRooms
from user.models import User


class Review(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.URLField(max_length=500, blank=True, null=True)  # URLField로 변경
    on_main = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    taro_chat_room = models.ForeignKey(TaroChatRooms, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name="reviews")

    def increase_view_count(self) -> None:
        """조회수를 1 증가시키는 메서드"""
        self.view_count += 1
        self.save(update_fields=["view_count"])

    def __str__(self) -> str:
        return self.title
