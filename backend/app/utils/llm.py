from typing import Optional, List, Any
import os
from google import genai
from google.genai import types
from app.core.config import settings
from app.ingestion.embeddings import get_genai_client

FALLBACK_MODELS = [
    settings.GEMINI_MODEL,
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-flash-latest",
    "gemini-3.8-flash"
]

def generate_with_fallback(
    contents: Any,
    config: Optional[types.GenerateContentConfig] = None,
    preferred_model: Optional[str] = None
) -> Any:
    """
    Generate content with automatic model fallback to guard against transient 503 spikes.
    """
    client = get_genai_client()
    
    models_to_try = []
    if preferred_model:
        models_to_try.append(preferred_model)
    for m in FALLBACK_MODELS:
        if m and m not in models_to_try:
            models_to_try.append(m)
            
    last_error = None
    for model_name in models_to_try:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config,
            )
            return response
        except Exception as e:
            err_msg = str(e)
            print(f"Model {model_name} failed: {err_msg[:120]}")
            last_error = e
            if any(code in err_msg for code in ["503", "UNAVAILABLE", "404", "NOT_FOUND", "ResourceExhausted"]):
                continue
            raise e
            
    raise RuntimeError(f"All candidate Gemini models failed. Last error: {last_error}")
