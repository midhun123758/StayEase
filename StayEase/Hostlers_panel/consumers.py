import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import RoomChatGroup, RoomChatMessage


class RoomGroupConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.group_id = self.scope["url_route"]["kwargs"]["group_id"]

        self.room_group_name = f"room_chat_{self.group_id}"

        user = self.scope["user"]

        print("CONNECTED USER:", user)

        # Authentication check
        if user.is_anonymous:

            print("USER IS ANONYMOUS")

            await self.close()
            return

        # Room access check
        has_access = await self.check_room_access(user)

        print("HAS ACCESS:", has_access)

        if not has_access:

            print("ACCESS DENIED")

            await self.close()
            return

        # Join websocket group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print("WEBSOCKET CONNECTED SUCCESSFULLY")

        # Notify joined
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_joined",
                "username": user.username,
            }
        )

    async def disconnect(self, close_code):

        user = self.scope["user"]

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Notify left
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "user_left",
                "username": user.username,
            }
        )

    async def receive(self, text_data):

        data = json.loads(text_data)

        message = data.get("message")

        if not message:
            return

        sender = self.scope["user"]

        # Save message
        saved_message = await self.save_message(
            sender,
            message
        )

        # Broadcast message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": saved_message.message,
                "sender": sender.username,
                "message_id": saved_message.id,
                "created_at": str(saved_message.created_at),
            }
        )

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "type": "chat_message",
            "message": event["message"],
            "sender": event["sender"],
            "message_id": event["message_id"],
            "created_at": event["created_at"],
        }))

    async def user_joined(self, event):

        await self.send(text_data=json.dumps({
            "type": "user_joined",
            "username": event["username"],
        }))

    async def user_left(self, event):

        await self.send(text_data=json.dumps({
            "type": "user_left",
            "username": event["username"],
        }))

    @sync_to_async
    def save_message(self, sender, message):

        group = RoomChatGroup.objects.get(
            id=self.group_id
        )

        return RoomChatMessage.objects.create(
            group=group,
            sender=sender,
            message=message
        )

    @sync_to_async
    def check_room_access(self, user):

        return RoomChatGroup.objects.filter(
            id=self.group_id,
            members__user=user
        ).exists()