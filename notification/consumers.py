import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

from .models import Notification, NotiUser


class NotificationConsumer(AsyncWebsocketConsumer):  # type: ignore
    async def connect(self) -> None:
        """사용자가 웹소켓에 연결하면 실행"""
        if self.scope["user"] is AnonymousUser:
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"notifications_{self.user.id}"

            # 채널 그룹에 추가
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code) -> None:  # type: ignore
        """웹소켓 연결 해제 시 실행"""
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data: str = None, bytes_data: bytes = None) -> None:  # type: ignore
        """클라이언트에서 메시지를 보낼 때 실행"""
        data = json.loads(text_data)
        if data.get("command") == "mark_as_read":
            await self.mark_notification_as_read(data.get("notification_id"))

    async def send_notification(self, event) -> None:  # type: ignore
        """새로운 알림이 생성될 때 실행"""
        notification = event["notification"]
        await self.send(text_data=json.dumps(notification))

    @sync_to_async
    def mark_notification_as_read(self, notification_id) -> None:  # type: ignore
        """알림을 읽음 처리"""
        try:
            noti_user = NotiUser.objects.get(user=self.user, notification_id=notification_id)
            noti_user.is_read = True
            noti_user.save()
        except NotiUser.DoesNotExist:
            pass
