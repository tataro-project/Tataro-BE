import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.template.context_processors import static

from notification.models import Notification, NotiUser

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):  # type: ignore
    async def connect(self):  # type: ignore
        """WebSocket 연결 시 실행"""
        self.user = self.scope["user"]
        if self.user.is_authenticated:
            print("connect", self.user.id)
            await self.accept()
            await self.send_unread_notifications()  # type: ignore
        else:
            await self.close()

    async def disconnect(self, close_code):  # type: ignore
        """WebSocket 연결 해제 시 실행"""
        pass

    async def receive(self, text_data: str):  # type: ignore
        """클라이언트에서 메시지를 받을 때 실행"""
        print("receive", text_data)
        try:
            data = json.loads(text_data)
            if data.get("action") == "mark_as_read":
                notification_id = data.get("notification_id")
                await self.mark_notification_as_read(notification_id)  # type: ignore

        except json.JSONDecodeError as e:
            print("JSON decode error:", str(e))
            await self.send(text_data=json.dumps({"error": "Invalid JSON format", "details": str(e)}))
        except KeyError as e:
            print("Key error:", str(e))
            await self.send(text_data=json.dumps({"error": "Missing required field", "details": str(e)}))
        except Exception as e:
            print("Unexpected error:", str(e))
            await self.send(text_data=json.dumps({"error": "An unexpected error occurred", "details": str(e)}))
            # 심각한 오류 발생 시 연결 종료

    async def send_unread_notifications(self):  # type: ignore
        """읽지 않은 알림 목록을 전송"""
        print("send_unread_notifications", self.user.id)
        if not self.user.is_authenticated:
            print("send_unread_notifications : 인증되지 않음.")
            return  # 인증되지 않은 사용자는 알림을 받을 수 없음

        unread_notifications = await database_sync_to_async(self.get_unread_notifications)(self.user)

        notifications_data = [
            {
                "id": noti.id,
                "title": noti.title,
                "url": noti.content,
                "category": noti.category.name if noti.category else None,
            }
            for noti in unread_notifications
        ]

        await self.send(
            text_data=json.dumps({"notifications": notifications_data}, ensure_ascii=False)
        )  # 여기서 ensure_ascii=False 설정을 안하면 인코딩 문제 발생 했음.

    async def mark_notification_as_read(self, notification_id):  # type: ignore
        """특정 알림을 읽음 처리"""
        try:
            notiuser = await sync_to_async(NotiUser.objects.get)(notification_id=notification_id)
            if notiuser:
                if self.user.id not in notiuser.read_users:
                    notiuser.read_users.append(self.user.id)
                    await sync_to_async(notiuser.save)()
                    await self.send(
                        text_data=json.dumps({"status": "marked_as_read", "notification_id": notification_id})
                    )
                else:
                    await self.send(
                        text_data=json.dumps({"status": "already_read", "notification_id": notification_id})
                    )
        except NotiUser.DoesNotExist:
            await self.send(text_data=json.dumps({"error": "NotiUser not found"}))

    def get_unread_notifications(self, user):  # type: ignore
        return list(
            Notification.objects.filter(is_active=True)
            .exclude(notiusers__read_users__contains=[user.id])
            .select_related("category")
        )
