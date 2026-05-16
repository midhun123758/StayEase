from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Hostler, RoomChatGroup


@receiver(post_save, sender=Hostler)
def auto_add_hostlers_to_room_group(sender, instance, created, **kwargs):

    if not instance.room or not instance.hostel:
        return

    group, created = RoomChatGroup.objects.get_or_create(
        room=instance.room,
        defaults={
            "hostel": instance.hostel
        }
    )

    same_room_hostlers = Hostler.objects.filter(
        room=instance.room,
        is_active=True
    )

    group.members.set(same_room_hostlers)