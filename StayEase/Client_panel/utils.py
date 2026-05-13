from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_client_notification(user_id, message, notification_type, data=None):

    channel_layer = get_channel_layer()

    async_to_sync(channel_layer.group_send)(
        f"notify_{user_id}",
        {
            "type": "send_notification",
            "notification_type": notification_type,
            "message": message,
            "data": data or {},
        }
    )