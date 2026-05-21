# hostels/signals.py
import pika, json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Hostel

def publish(event_type, payload):
    try:
        conn = pika.BlockingConnection(
            pika.URLParameters("amqp://guest:guest@rabbitmq:5672/")
        )
        ch = conn.channel()
        ch.queue_declare(queue="hostel.events", durable=True)
        ch.basic_publish(
            exchange="",
            routing_key="hostel.events",
            body=json.dumps({"type": event_type, **payload}),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        conn.close()
        print(f"✅ Event published: {event_type}")
    except Exception as e:
        print(f"❌ RabbitMQ error: {e}")

@receiver(post_save, sender=Hostel)
def on_hostel_saved(sender, instance, **kwargs):
    publish("hostel.upserted", {
        "id": instance.id,
        "text": instance.to_text(),
        "metadata": instance.to_metadata(),
    })

@receiver(post_delete, sender=Hostel)
def on_hostel_deleted(sender, instance, **kwargs):
    publish("hostel.deleted", {"id": instance.id})