from app.agents.state import AgentState
from app.rag.retriever import retrieve_hybrid
from app.verification.rule_engine import evaluate_scheme_eligibility
from app.models.eligibility import EligibilityRule
from app.models.scheme import Scheme
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
import json
import os

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def coordinator_node(state: AgentState) -> AgentState:
    user_query = state.get("user_query")
    user_profile = state.get("user_profile")
    
    system_prompt = """You are an intent parser for a Government Scheme Analyzer.
Extract the following from the user's query:
- search_keywords: Keywords to search for schemes.
- state_filter: State mentioned, or null.
- department_filter: Department mentioned, or null.
Return exactly JSON format with keys: search_keywords, state_filter, department_filter."""

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=f"{system_prompt}\n\nUser Query: {user_query}",
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            ),
        )
        parsed = json.loads(response.text)
    except Exception as e:
        print(f"Coordinator error: {e}")
        parsed = {"search_keywords": user_query, "state_filter": None, "department_filter": None}
    
    state_filter = parsed.get("state_filter")
    if not state_filter and user_profile and user_profile.state:
        state_filter = user_profile.state
        
    return {
        "search_keywords": parsed.get("search_keywords", user_query),
        "state_filter": state_filter,
        "department_filter": parsed.get("department_filter")
    }

def get_retrieval_node(db: Session):
    def retrieval_node(state: AgentState) -> AgentState:
        keywords = state.get("search_keywords", state.get("user_query"))
        chunks = retrieve_hybrid(
            db=db,
            query=keywords,
            state_filter=state.get("state_filter"),
            department_filter=state.get("department_filter"),
            top_k=10
        )
        return {"retrieved_chunks": chunks}
    return retrieval_node

def get_eligibility_node(db: Session):
    def eligibility_node(state: AgentState) -> AgentState:
        profile = state.get("user_profile")
        if not profile:
            return {"eligibility_results": {}}
            
        retrieved_chunks = state.get("retrieved_chunks", [])
        
        if not retrieved_chunks:
            schemes = db.query(Scheme).filter(Scheme.is_active == True).all()
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
