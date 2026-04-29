import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import HostelMessage, ChatRoom
from Base_Panel.models import Hostel

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.hostel_id = self.scope['url_route']['kwargs']['room_id']
        user_id = self.scope['url_route']['kwargs']['user_id']
        
        self.user = await self.get_user(user_id)

        try:
            chatroom = await self.get_or_create_chatroom()
            self.chatroom_id = chatroom.id
            self.room_group = f"chat_{self.chatroom_id}"
            
            await self.channel_layer.group_add(self.room_group, self.channel_name)
            await self.accept()
        except Exception as e:
            print(f"WebSocket Connection error: {e}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group'):
            await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_text = data.get("message")
        if not message_text:
            return

        msg_data = await self.save_and_get_data(message_text)

        await self.channel_layer.group_send(
            self.room_group,
            {
                "type": "chat_message",
                "message": msg_data["message"],
                "sender": msg_data["sender_name"],
                "sender_id": msg_data["sender_id"],
                "timestamp": msg_data["timestamp"],
                "tempId": data.get("tempId") # Echo back for React Optimistic UI
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user(self, user_id):
        return User.objects.get(id=user_id)

    @database_sync_to_async
    def get_or_create_chatroom(self):
        from Base_Panel.models import Hostel
        hostel = Hostel.objects.get(id=self.hostel_id)
        room, created = ChatRoom.objects.get_or_create(
          hostel=hostel,
          client=self.user,
          defaults={'owner': hostel.owner})
        return room
        

    @database_sync_to_async
    def save_and_get_data(self, message_text):
     
        room = ChatRoom.objects.get(id=self.chatroom_id)
        
      
        if self.user.id == room.client.id:
            receiver = room.owner
        else:
            receiver = room.client

        msg = HostelMessage.objects.create(
            chatroom=room,
            sender=self.user,
            receiver=receiver,
            message=message_text
        )
        
        return {
            "message": msg.message,
            "sender_name": self.user.username,
            "sender_id": self.user.id,
            "timestamp": msg.created_at.isoformat()
        }
    
    # consumers.py

@database_sync_to_async
def save_message_safely(self, message_text):
    from .models import ChatRoom, HostelMessage
    from App.models import User # Adjust import path as needed
    
    room = ChatRoom.objects.select_related('client', 'owner').get(id=self.chatroom_id)
    if self.user.id == room.client.id:
        target_receiver = room.owner
    else:
        target_receiver = room.client

    return HostelMessage.objects.create(
        chatroom=room,
        sender=self.user,
        receiver=target_receiver,
        message=message_text
    )