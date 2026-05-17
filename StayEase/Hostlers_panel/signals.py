from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from Base_Panel.models import Hostler

from .models import RoomChatGroup


@receiver(post_save, sender=Hostler)
def auto_add_hostlers_to_room_group(
    sender,
    instance,
    created,
    **kwargs
):

    # No room assigned
    if not instance.room or not instance.hostel:
        return

    # Create or get room chat group
    group, created = RoomChatGroup.objects.get_or_create(
        room=instance.room,
        defaults={
            "hostel": instance.hostel
        }
    )

    # Get active hostlers in same room
    same_room_hostlers = Hostler.objects.filter(
        room=instance.room,
        is_active=True
    )

    # Update members
    group.members.set(same_room_hostlers)

    # Delete group if empty
    if same_room_hostlers.count() == 0:

        group.delete()


@receiver(post_delete, sender=Hostler)
def delete_empty_room_chat_group(
    sender,
    instance,
    **kwargs
):

    if not instance.room:
        return

    try:

        group = RoomChatGroup.objects.get(
            room=instance.room
        )

        remaining_hostlers = Hostler.objects.filter(
            room=instance.room,
            is_active=True
        )

        # Delete empty room group
        if remaining_hostlers.count() == 0:

            group.delete()

        # Update remaining members
        else:

            group.members.set(
                remaining_hostlers
            )

    except RoomChatGroup.DoesNotExist:

        pass