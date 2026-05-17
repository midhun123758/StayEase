from django.db import models
from django.conf import settings
from App.models import User
from Base_Panel.models import AssignedMeal, Hostel, Hostler, Room
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
    


class MealResponse(models.Model):

    RESPONSE_CHOICES = (
        ("WANT", "Want"),
        ("NOT_WANT", "Not Want"),
    )

    assigned_meal = models.ForeignKey(
        AssignedMeal,
        on_delete=models.CASCADE,
        related_name="responses"
    )

    hostler = models.ForeignKey(
        Hostler,
        on_delete=models.CASCADE,
        related_name="meal_responses"
    )

    response = models.CharField(
        max_length=20,
        choices=RESPONSE_CHOICES
    )

    created_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        unique_together = ("assigned_meal", "hostler")

    def __str__(self):
        return f"{self.hostler} - {self.response}"
    


