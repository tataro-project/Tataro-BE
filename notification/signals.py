from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification, NotiUser


@receiver(post_save, sender=Notification)
def send_notification_to_users(sender, instance, created, **kwargs) -> None:  # type: ignore
    """새로운 알림이 생성되면 해당 사용자에게 웹소켓으로 전송"""
    if created:
        noti_users = NotiUser.objects.filter(notification=instance)

        channel_layer = get_channel_layer()
        for noti_user in noti_users:
            group_name = f"notifications_{noti_user.user.id}"
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "send_notification",
                    "notification": {
                        "id": instance.id,
                        "title": instance.title,
                        "content": instance.content,
                        "is_read": noti_user.is_read,
                    },
                },
            )
