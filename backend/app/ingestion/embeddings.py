from typing import List, Optional
import os
from google import genai
from app.core.config import settings

_client: Optional[genai.Client] = None

def get_genai_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment or settings.")
        _client = genai.Client(api_key=api_key)
    return _client

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    client = get_genai_client()
    try:
        response = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=texts,
        )
        embeddings = [e.values for e in response.embeddings]
        return embeddings
    except Exception as e:
        print(f"Error generating embeddings with Gemini ({settings.EMBEDDING_MODEL}): {e}")
        raise

def generate_embedding(text: str) -> List[float]:
    if not text:
        return [0.0] * settings.EMBEDDING_DIM
    client = get_genai_client()
    try:
        response = client.models.embed_content(
            model=settings.EMBEDDING_MODEL,
            contents=text,
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Error generating single embedding with Gemini ({settings.EMBEDDING_MODEL}): {e}")
        raise
