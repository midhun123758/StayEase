import asyncio, json, logging
import aio_pika
from app.ai_service import embed_and_store, delete_from_vector, setup_collection
from app.config import RABBITMQ_URL

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

async def main():
    await setup_collection()

    # RabbitMQ ready ആകുന്നത് വരെ retry ചെയ്യുന്നു
    while True:
        try:
            conn = await aio_pika.connect_robust(
                RABBITMQ_URL,
                reconnect_interval=5,   # disconnect ആയാൽ 5s-ൽ reconnect
            )
            break
        except Exception as e:
            log.warning(f"⏳ RabbitMQ not ready, retrying in 5s... ({e})")
            await asyncio.sleep(5)

    log.info("✅ Connected to RabbitMQ!")

    async with conn:
        ch = await conn.channel()
        q  = await ch.declare_queue("hostel.events", durable=True)
        log.info("👂 Worker listening for hostel events...")
        async with q.iterator() as msgs:
            async for msg in msgs:
                async with msg.process():
                    data = json.loads(msg.body)
                    log.info(f"📩 Event received: {data['type']}")
                    try:
                        if data["type"] == "hostel.upserted":
                            await embed_and_store(
                                data["id"],
                                data["text"],
                                data["metadata"],
                            )
                        elif data["type"] == "hostel.deleted":
                            await delete_from_vector(data["id"])
                    except Exception as e:
                        log.error(f"❌ Error processing event: {e}")

if __name__ == "__main__":
    asyncio.run(main())