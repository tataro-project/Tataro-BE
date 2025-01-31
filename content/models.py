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
    img_url = models.CharField(max_length=255)
    on_main = models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    # Other fields...


class Notice(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.CharField(max_length=255)
    order = models.IntegerField(default=None)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notices")
    # Other fields...


class Notification(BaseModel):
    title = models.CharField(max_length=255)
    content = models.TextField()
    img_url = models.CharField(max_length=255)
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
