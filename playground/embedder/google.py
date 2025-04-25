import os
from agno.embedder.google import GeminiEmbedder

def get_google_embedder()->GeminiEmbedder:
    embedder=GeminiEmbedder(
        id=os.getenv("GEMINI_EMBEDDER_MODEL_ID", "models/text-embedding-004"),
        dimensions=int(os.getenv("GEMINI_EMBEDDER_DIMENSIONS", "768"))
    )
    return embedder