import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # Opcional: pode ser usado para comandos do frontend
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "link": event.get("link"),
            "notification_id": event.get("notification_id"),
        })) 