from django.db import models
from django.conf import settings
from App.models import User
from Base_Panel.models import Hostel, Hostler, Room
# Create your models here.
class Notification(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )

    title = models.CharField(max_length=255)

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class RoomChatGroup(models.Model):
    hostel = models.ForeignKey(Hostel,on_delete=models.CASCADE,related_name="room_chat_groups")

    room = models.OneToOneField(Room,on_delete=models.CASCADE,related_name="chat_group")

    members = models.ManyToManyField(Hostler,related_name="room_chat_groups",blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.hostel.name} - Room {self.room.room_number} Chat"
    

class RoomChatMessage(models.Model):
    group = models.ForeignKey(
        RoomChatGroup,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,
on_delete=models.CASCADE,
        related_name="room_chat_messages"
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} - {self.group.room.room_number}"