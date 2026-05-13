import boto3
from django.conf import settings
import uuid
def generate_presigned_url(file_type):
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )

    file_name = f"documents/{uuid.uuid4()}"

    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": file_name
        },
        ExpiresIn=300
    )

    file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_name}"

    return url, file_url


from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def send_live_notification(user_id, notification_type, message, data=None):
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