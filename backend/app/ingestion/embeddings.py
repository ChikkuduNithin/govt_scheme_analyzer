from typing import List
import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_embeddings(texts: List[str]) -> List[List[float]]:
    if not texts:
        return []
    try:
        response = client.models.embed_content(
            model='text-embedding-004',
            contents=texts,
        )
        return [e.values for e in response.embeddings]
    except Exception as e:
        print(f"Error generating embeddings with Gemini: {e}")
        return [[0.0] * 768 for _ in texts]

def generate_embedding(text: str) -> List[float]:
    try:
        response = client.models.embed_content(
            model='text-embedding-004',
            contents=text,
        )
        return response.embeddings[0].values
    except Exception as e:
        print(f"Error generating single embedding with Gemini: {e}")
        return [0.0] * 768
