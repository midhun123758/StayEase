import os
from dotenv import load_dotenv
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
RABBITMQ_URL   = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq/")
QDRANT_URL     = os.getenv("QDRANT_URL", "http://qdrant:6333")