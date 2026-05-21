from fastapi import FastAPI
from contextlib import asynccontextmanager
from google import genai
from app.config import GEMINI_API_KEY
from app.ai_service import search_hostels, setup_collection

client = genai.Client(api_key=GEMINI_API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_collection()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/ask")
async def ask(question: str):
    results = await search_hostels(question)

    context = "\n".join([
        f"- {r.payload['name']}, {r.payload['city']} | "
        f"Rooms: {r.payload['rooms_available']} | "
        f"Mess: {'Yes' if r.payload['mess_service'] else 'No'} | "
        f"Contact: {r.payload['contact_number']}"
        for r in results
    ])

    reply = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=(
            f"You are a hostel finder assistant for StayEase.\n"
            f"Answer using only these hostels:\n{context}\n\n"
            f"Question: {question}"
        ),
    )
    return {
        "answer": reply.text,
        "hostels": [r.payload for r in results],
    }