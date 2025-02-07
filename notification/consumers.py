import json

from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):  # type: ignore
    async def connect(self) -> None:
        self.group_name = f"user_{self.scope['user'].id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code) -> None:  # type: ignore
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data) -> None:  # type: ignore
        data = json.loads(text_data)
        message = data.get("message", "")
        await self.send(text_data=json.dumps({"message": message}))

    async def send_notification(self, event) -> None:  # type: ignore
        await self.send(text_data=json.dumps(event["data"]))
