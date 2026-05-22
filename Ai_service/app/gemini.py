from google import genai
from app.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
You are a helpful assistant for StayEase, a hostel booking platform.
Help users with hostel questions, bookings, pricing and recommendations.
Be friendly and concise.
"""

def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-preview",
        contents=SYSTEM_PROMPT + "\n\n" + prompt,
    )
    return response.text