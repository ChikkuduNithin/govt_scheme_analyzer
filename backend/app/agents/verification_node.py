from typing import Dict, List, Any
import json
import os
from google import genai
from google.genai import types
from app.agents.state import AgentState

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_claims_and_verify(scheme_id: int, eval_result: Dict, retrieved_chunks: List[Dict]) -> Dict:
    status = eval_result["status"]
    satisfied = [r.description for r in eval_result["details"]["satisfied"]]
    not_satisfied = [r.description for r in eval_result["details"]["not_satisfied"]]
    
    scheme_chunks = [c for c in retrieved_chunks if c["scheme_id"] == scheme_id]
    context_text = "\n\n".join([f"Source {i+1} (Page {c.get('page_number', '?')}):\n{c['text']}" for i, c in enumerate(scheme_chunks)])
    
    system_prompt = """You are a strict Verification Agent for a Government Scheme Analyzer.
Your job is to verify eligibility claims against the provided official documents.
For each claim, determine if it is VERIFIED, CONTRADICTED, or UNSUPPORTED based *only* on the provided document text.
Provide a clear, readable summary.

Return exactly JSON format with keys 'summary' and 'claims'.
'claims' is an array of objects with keys: 'claim', 'status' (VERIFIED, CONTRADICTED, UNSUPPORTED), 'evidence_citation', and 'reasoning'."""

    user_prompt = f"""
Calculated Eligibility Status: {status}

Satisfied Conditions:
{json.dumps(satisfied, indent=2)}

Failed Conditions:
{json.dumps(not_satisfied, indent=2)}

Official Scheme Documents (Context):
{context_text}
"""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_prompt}\n\n{user_prompt}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Verification error: {e}")
        return {
            "summary": "Verification failed due to an error.",
            "claims": []
        }

def verification_node(state: AgentState) -> AgentState:
    eligibility_results = state.get("eligibility_results", {})
    retrieved_chunks = state.get("retrieved_chunks", [])
    
    verified_results = {}
    for scheme_id, eval_result in eligibility_results.items():
        verification = generate_claims_and_verify(scheme_id, eval_result, retrieved_chunks)
        eval_result["verification"] = verification
        verified_results[scheme_id] = eval_result
        
    return {"eligibility_results": verified_results}
