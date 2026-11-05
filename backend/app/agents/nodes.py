import json
import os
import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from google.genai import types

from app.core.config import settings
from app.agents.state import AgentState
from app.rag.retriever import retrieve_hybrid
from app.verification.rule_engine import evaluate_scheme_eligibility
from app.models.eligibility import EligibilityRule
from app.models.scheme import Scheme
from app.ingestion.embeddings import get_genai_client

def fast_heuristic_extract(query: str) -> Dict[str, Any]:
    lowered = query.lower()
    
    # State detection
    detected_state = None
    state_map = {
        "telangana": "Telangana",
        "osmania": "Telangana",
        "hyderabad": "Telangana",
        "andhra": "Andhra Pradesh",
        "tamil nadu": "Tamil Nadu",
        "chennai": "Tamil Nadu",
        "karnataka": "Karnataka",
        "bangalore": "Karnataka",
        "bengaluru": "Karnataka",
        "maharashtra": "Maharashtra",
        "mumbai": "Maharashtra",
        "pune": "Maharashtra",
        "west bengal": "West Bengal",
        "kolkata": "West Bengal",
        "rajasthan": "Rajasthan",
        "odisha": "Odisha"
    }
    for kw, st in state_map.items():
        if kw in lowered:
            detected_state = st
            break
            
    # Department detection
    detected_dept = None
    if any(k in lowered for k in ["scholarship", "degree", "college", "student", "matric", "university", "study"]):
        detected_dept = "Higher Education"
    elif any(k in lowered for k in ["farm", "crop", "kisan", "rythu", "seed", "tractor"]):
        detected_dept = "Agriculture"
    elif any(k in lowered for k in ["health", "hospital", "medical", "ayushman", "arogyasri", "treatment"]):
        detected_dept = "Health"
    elif any(k in lowered for k in ["pension", "old age", "senior", "widow"]):
        detected_dept = "Social Welfare"
        
    # Search keywords
    clean_words = [w for w in re.findall(r'\b[a-zA-Z]{3,}\b', query) if w.lower() not in {"the", "and", "for", "with", "from", "any", "are", "what", "can"}]
    search_keywords = " ".join(clean_words) if clean_words else query
    
    return {
        "search_keywords": search_keywords,
        "state_filter": detected_state,
        "department_filter": detected_dept
    }

def coordinator_node(state: AgentState) -> Dict[str, Any]:
    user_query = state.get("user_query", "")
    user_profile = state.get("user_profile")
    
    # Instant heuristic extraction as baseline
    heuristic = fast_heuristic_extract(user_query)
    
    # Try fast Gemini extraction if available (single attempt without long retry loops)
    try:
        client = get_genai_client()
        system_prompt = "Extract search_keywords, state_filter, department_filter as JSON from query."
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=f"{system_prompt}\nQuery: {user_query}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                max_output_tokens=150,
                temperature=0.1
            ),
        )
        text_resp = response.text.strip()
        if text_resp.startswith("```"):
            text_resp = re.sub(r"^```(?:json)?\s*|\s*```$", "", text_resp, flags=re.DOTALL)
        parsed = json.loads(text_resp)
        search_keywords = parsed.get("search_keywords") or heuristic["search_keywords"]
        state_filter = parsed.get("state_filter") or heuristic["state_filter"]
        department_filter = parsed.get("department_filter") or heuristic["department_filter"]
    except Exception as e:
        # Fall back to instant heuristic extraction
        search_keywords = heuristic["search_keywords"]
        state_filter = heuristic["state_filter"]
        department_filter = heuristic["department_filter"]
    
    if not state_filter and user_profile and getattr(user_profile, "state", None):
        state_filter = user_profile.state
        
    return {
        "search_keywords": search_keywords,
        "state_filter": state_filter,
        "department_filter": department_filter
    }

def get_retrieval_node(db: Session):
    def retrieval_node(state: AgentState) -> Dict[str, Any]:
        keywords = state.get("search_keywords") or state.get("user_query")
        chunks = retrieve_hybrid(
            db=db,
            query=keywords,
            state_filter=state.get("state_filter"),
            department_filter=state.get("department_filter"),
            top_k=5
        )
        return {"retrieved_chunks": chunks}
    return retrieval_node

def get_eligibility_node(db: Session):
    def eligibility_node(state: AgentState) -> Dict[str, Any]:
        profile = state.get("user_profile")
        if not profile:
            return {"eligibility_results": {}}
            
        retrieved_chunks = state.get("retrieved_chunks", [])
        
        if not retrieved_chunks:
            schemes = db.query(Scheme).filter(Scheme.is_active == True).limit(5).all()
            unique_scheme_ids = [s.id for s in schemes]
        else:
            unique_scheme_ids = list(set(chunk["scheme_id"] for chunk in retrieved_chunks))
        
        results = {}
        for scheme_id in unique_scheme_ids:
            rules = db.query(EligibilityRule).filter(EligibilityRule.scheme_id == scheme_id).all()
            if rules:
                eval_result = evaluate_scheme_eligibility(profile, rules)
                results[scheme_id] = eval_result
            else:
                results[scheme_id] = {
                    "status": "INSUFFICIENT_INFORMATION",
                    "details": {"satisfied": [], "not_satisfied": [], "unknown": []}
                }
                
        return {"eligibility_results": results}
    return eligibility_node
