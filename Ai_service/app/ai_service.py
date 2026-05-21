from google import genai

from qdrant_client import AsyncQdrantClient

from qdrant_client.models import (

    PointStruct,
    Distance,
    VectorParams

)

from app.config import (

    GEMINI_API_KEY,
    QDRANT_URL

)


client = genai.Client(

    api_key=GEMINI_API_KEY

)

qdrant = AsyncQdrantClient(

    url=QDRANT_URL

)

COLLECTION = "hostels"


async def setup_collection():

    existing = await qdrant.get_collections()

    names = [

        c.name

        for c in existing.collections

    ]

    if COLLECTION not in names:
        await qdrant.create_collection(
            collection_name=COLLECTION,

            vectors_config=VectorParams(

                size=3072,

                distance=Distance.COSINE

            ),

        )

        print("✅ Qdrant collection created")


def get_embedding(text: str) -> list[float]:

    result = client.models.embed_content(

        model="gemini-embedding-001",

        contents=text,

    )

    return result.embeddings[0].values


async def embed_and_store(

    hostel_id: int,

    text: str,

    metadata: dict

):

    vector = get_embedding(text)

    await qdrant.upsert(

        collection_name=COLLECTION,

        points=[

            PointStruct(

                id=hostel_id,

                vector=vector,

                payload=metadata

            )

        ],

    )

    print(f"✅ '{metadata['name']}' stored in Qdrant!")


async def delete_from_vector(hostel_id: int):

    await qdrant.delete(

        collection_name=COLLECTION,

        points_selector=[hostel_id],

    )

    print(f"🗑️ Hostel {hostel_id} deleted from Qdrant")


async def search_hostels(question: str):

    vector = get_embedding(question)

    results = await qdrant.query_points(

        collection_name=COLLECTION,

        query=vector,

        limit=5,

        with_payload=True,

    )

    return results.points