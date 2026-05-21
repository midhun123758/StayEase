import pika
import json

def push_to_ai_queue(document_id, text_content):
    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    
    # Create the queue if it doesn't exist
    channel.queue_declare(queue='ai_tasks')
    
    # Format the data
    payload = {
        "id": str(document_id),
        "text": text_content
    }
    
    # Send it
    channel.basic_publish(
        exchange='',
        routing_key='ai_tasks',
        body=json.dumps(payload)
    )
    
    print(f"Success: Sent document {document_id} to RabbitMQ!")
    connection.close()