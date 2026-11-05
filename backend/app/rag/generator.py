from typing import List, Dict
import os
from google.genai import types
from app.core.config import settings
from app.utils.llm import generate_with_fallback

def generate_answer(query: str, retrieved_chunks: List[Dict]) -> str:
    """
    Generate a grounded, cited answer using Gemini based strictly on the retrieved document chunks.
    """
    if not retrieved_chunks:
        return "No relevant government scheme documents were found matching your query."
        
    context_blocks = []
    for idx, c in enumerate(retrieved_chunks):
        scheme_name = c.get("scheme_name", "Scheme")
        page = c.get("page_number", "?")
        text = c.get("text", "")
        context_blocks.append(f"[{idx + 1}] Scheme: {scheme_name} (Page {page}):\n{text}")
        
    context_str = "\n\n".join(context_blocks)
    
    prompt = f"""You are a helpful and accurate Government Scheme Advisor.
Answer the citizen's query based ONLY on the provided government scheme guidelines below.
Cite specific schemes and page numbers where applicable.
If the information is not present in the excerpts, clearly state that you don't have enough official information.

Official Scheme Excerpts:
{context_str}

Citizen Query:
{query}

Grounded Response:"""

    try:
        response = generate_with_fallback(
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating answer with Gemini: {e}")
        return f"Unable to generate response at this time. (Error: {e})"
