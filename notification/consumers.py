import json

from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

from notification.models import Notification, NotiUser

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):  # type: ignore
    async def connect(self):  # type: ignore
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            self.room_group_name = f"user_{self.user.id}_notifications"

            # Join room group
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)

            await self.accept()
            await self.send_unread_notifications()  # type: ignore
        else:
            await self.close()

    async def disconnect(self, close_code):  # type: ignore
        # Leave room group
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def send_unread_notifications(self):  # type: ignore
        unread_notifications = await database_sync_to_async(self.get_unread_notifications)(self.user)
        notifications_data = [
            {
                "id": noti.id,
                "title": noti.title,
                "url": noti.content,
                "category": noti.category if noti.category else None,
                "created_at": noti.created_at,
            }
            for noti in unread_notifications
        ]
        await self.send(text_data=json.dumps({"notifications": notifications_data}, ensure_ascii=False))

    # # 클라이언트가 보낸 알림을 받음.
    # async def receive(self, text_data):  # type: ignore
    #     try:
    #         data = json.loads(text_data)
    #         if data.get("action") == "mark_as_read":
    #             notification_id = data.get("notification_id")
    #             await self.mark_notification_as_read(notification_id)
    #     except json.JSONDecodeError as e:
    #         await self.send(text_data=json.dumps({"error": "Invalid JSON format", "details": str(e)}))
    #     except Exception as e:
    #         await self.send(text_data=json.dumps({"error": "An unexpected error occurred", "details": str(e)}))
    #
    # async def mark_notification_as_read(self, notification_id):  # type: ignore
    #     """특정 알림을 읽음 처리"""
    #     try:
    #         notiuser = await sync_to_async(NotiUser.objects.get)(notification_id=notification_id)
    #         if notiuser:
    #             if self.user.id not in notiuser.read_users:
    #                 notiuser.read_users.append(self.user.id)
    #                 await sync_to_async(notiuser.save)()
    #                 await self.send(
    #                     text_data=json.dumps({"status": "marked_as_read", "notification_id": notification_id})
    #                 )
    #             else:
    #                 await self.send(
    #                     text_data=json.dumps({"status": "already_read", "notification_id": notification_id})
    #                 )
    #     except NotiUser.DoesNotExist:
    #         await self.send(text_data=json.dumps({"error": "NotiUser not found"}))

    def get_unread_notifications(self, user):  # type: ignore
        return list(
            Notification.objects.filter(is_active=True)
            .exclude(notiusers__read_users__contains=[user.id])
            .select_related("user")  # 'category' 대신 'user'만 사용
            .order_by("-created_at")
        )

    async def new_notification(self, event):  # type: ignore
        # 새 알림을 클라이언트에게 전송
        notification_data = event["notification"]
        await self.send(text_data=json.dumps({"type": "new_notification", "notification": notification_data}))


def send_notification(user_id, notification_data):  # type: ignore
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}_notifications", {"type": "new_notification", "notification": notification_data}
    )
