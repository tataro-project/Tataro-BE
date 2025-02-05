from django.db import models

from user.models import User


class BaseModel(models.Model):
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Review(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.URLField(max_length=500, blank=True, null=True)  # URLField로 변경
    on_main = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")

    def increase_view_count(self) -> None:
        """조회수를 1 증가시키는 메서드"""
        self.view_count += 1
        self.save(update_fields=["view_count"])

    def __str__(self) -> str:
        return self.title


class Notice(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.URLField(max_length=500, blank=True, null=True)  # URLField로 변경
    order = models.IntegerField(blank=True, null=True, default=None)  # None 허용
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notices")

    def __str__(self) -> str:
        return self.title


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    # Other fields...


class NotiUser(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notiusers")
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name="notiusers")
    is_read = models.BooleanField(default=False)


class FAQ(BaseModel):
    question = models.TextField()
    answer = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="faqs")
