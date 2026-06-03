# from fastapi import FastAPI
# from contextlib import asynccontextmanager
# from google import genai
# from app.config import GEMINI_API_KEY
# from app.ai_service import search_hostels, setup_collection

# client = genai.Client(api_key=GEMINI_API_KEY)

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     await setup_collection()
#     yield

# app = FastAPI(lifespan=lifespan)

# @app.get("/health")
# async def health():
#     return {"status": "ok"}

# @app.post("/ask")
# async def ask(question: str):
#     results = await search_hostels(question)

#     context = "\n".join([
#         f"- {r.payload['name']}, {r.payload['city']} | "
#         f"Rooms: {r.payload['rooms_available']} | "
#         f"Mess: {'Yes' if r.payload['mess_service'] else 'No'} | "
#         f"Contact: {r.payload['contact_number']}"
#         for r in results
#     ])

#     reply = client.models.generate_content(
#         model="gemini-2.5-flash",
#         contents=(
#             f"You are a hostel finder assistant for StayEase.\n"
#             f"Answer using only these hostels:\n{context}\n\n"
#             f"Question: {question}"
#         ),
#     )
#     return {
#         "answer": reply.text,
#         "hostels": [r.payload for r in results],
#     }

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from google import genai

from app.config import GEMINI_API_KEY

from app.ai_service import (

    search_hostels,
    setup_collection

)


# -----------------------------------------
# Gemini Client
# -----------------------------------------

client = genai.Client(

    api_key=GEMINI_API_KEY

)


# -----------------------------------------
# App Lifespan
# -----------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):

    await setup_collection()

    yield


app = FastAPI(

    lifespan=lifespan

)


# -----------------------------------------
# CORS
# -----------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173",

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],

)


# -----------------------------------------
# Health Check
# -----------------------------------------

@app.get("/health")
async def health():

    return {

        "status": "ok"

    }


# -----------------------------------------
# AI Chat Endpoint
# -----------------------------------------

@app.post("/ask")
async def ask(question: str):

    try:

        # -----------------------------------------
        # Search from Qdrant
        # -----------------------------------------

        results = await search_hostels(question)


        # -----------------------------------------
        # No Results
        # -----------------------------------------

        if not results:

            return {

                "answer": "No matching hostels found.",

                "hostels": []

            }


        # -----------------------------------------
        # Build Context
        # -----------------------------------------

        context = "\n".join([

            f"""
            Hostel Name: {r.payload['name']}
            City: {r.payload['city']}
            State: {r.payload['state']}
            Location: {r.payload['location']}
            Rooms Available: {r.payload['rooms_available']}
            Mess Service: {'Yes' if r.payload['mess_service'] else 'No'}
            Contact: {r.payload['contact_number']}
            """

            for r in results

        ])


        # -----------------------------------------
        # Gemini Response
        # -----------------------------------------

        reply = client.models.generate_content(

            model="gemini-3.1-flash-lite",

            contents=(

                f"""
                You are StayEase AI Assistant.

                Your job:
                - Recommend hostels
                - Answer naturally
                - Use ONLY provided hostel data
                - Do NOT invent hostel information

                Hostel Data:
                {context}

                User Question:
                {question}
                """

            ),

        )


        # -----------------------------------------
        # API Response
        # -----------------------------------------

        return {

            "answer": reply.text,

            "hostels": [

                r.payload

                for r in results

            ]

        }


    # -----------------------------------------
    # Error Handling
    # -----------------------------------------

    except Exception as e:


        print("❌ AI Error:", str(e))

        return {

           "answer": str(e),

            "hostels": []

         }