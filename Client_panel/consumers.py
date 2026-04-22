import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name
        )
        await self.accept()
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name
        )

async def receive(self, text_data): 
    try:
        data = json.loads(text_data)
        
        # Use .get() to provide a fallback value instead of crashing
        message = data.get('message', '')
        sender = data.get('sender', 'Anonymous')

        # Broadcast to the group
        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                "message": message,
                "sender": sender
            }
        )
    except Exception as e:
        print(f"Error in receive: {e}")
        # Optionally send an error back to the frontend
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender": event["sender"]
        }))