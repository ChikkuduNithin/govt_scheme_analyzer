import json
import asyncio
from datetime import date
from types import SimpleNamespace
from typing import Any, Dict, AsyncGenerator
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api import deps
from app.models.scheme import Scheme
from app.models.user import User
from app.services import user_service
from app.agents.workflow import create_agent_workflow
from pydantic import BaseModel

class AnalyzeRequest(BaseModel):
    query: str

router = APIRouter()

def _parse_income(text: str):
    lowered = text.lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lakhs|lac|lacs|k|thousand|crore|crores)\b", lowered)
    if match:
        amount = float(match.group(1))
        unit = match.group(2)
        if unit in {"lakh", "lakhs", "lac", "lacs"}:
            return amount * 100000
        if unit in {"k", "thousand"}:
            return amount * 1000
        if unit in {"crore", "crores"}:
            return amount * 10000000

    direct = re.search(r"(?:income|salary|earning|earn)\D{0,20}(\d{5,9})", lowered)
    if direct:
        return float(direct.group(1))
    return None

def _parse_age(text: str):
    match = re.search(r"\b(\d{1,2})\s*(?:year|years|yr|yrs)?\s*old\b", text.lower())
    if not match:
        match = re.search(r"\bage\D{0,5}(\d{1,2})\b", text.lower())
    if not match:
        return None

    age = int(match.group(1))
    today = date.today()
    return date(today.year - age, today.month, today.day)

def _apply_query_overrides(profile, query: str):
    data: Dict[str, Any] = {
        "id": profile.id,
        "user_id": profile.user_id,
        "full_name": profile.full_name,
        "date_of_birth": profile.date_of_birth,
        "gender": profile.gender,
        "state": profile.state,
        "district": profile.district,
        "annual_income": profile.annual_income,
        "occupation": profile.occupation,
        "employment_status": profile.employment_status,
        "education_level": profile.education_level,
        "category": profile.category,
        "disability_status": profile.disability_status,
    }
    overrides: Dict[str, Any] = {}
    lowered = query.lower()

    income = _parse_income(query)
    if income is not None:
        data["annual_income"] = income
        overrides["annual_income"] = income

    dob = _parse_age(query)
    if dob is not None:
        data["date_of_birth"] = dob
        overrides["age"] = date.today().year - dob.year

    for state in ["Telangana", "Andhra Pradesh", "Tamil Nadu", "Karnataka", "Maharashtra", "West Bengal", "Rajasthan", "Odisha"]:
        if state.lower() in lowered:
            data["state"] = state
            overrides["state"] = state
            break

    for category in ["SC", "ST", "OBC", "Minority", "General"]:
        if re.search(rf"\b{re.escape(category.lower())}\b", lowered):
            data["category"] = category
            overrides["category"] = category
            break

    if "female" in lowered or "woman" in lowered or "girl" in lowered:
        data["gender"] = "Female"
        overrides["gender"] = "Female"
    elif "male" in lowered or "boy" in lowered:
        data["gender"] = "Male"
        overrides["gender"] = "Male"

    if "student" in lowered:
        data["employment_status"] = "Student"
        data["occupation"] = "Student"
        overrides["employment_status"] = "Student"
    elif "unemployed" in lowered:
        data["employment_status"] = "Unemployed"
        overrides["employment_status"] = "Unemployed"
    elif "self employed" in lowered or "self-employed" in lowered or "business" in lowered:
        data["employment_status"] = "Self-employed"
        overrides["employment_status"] = "Self-employed"

    return SimpleNamespace(**data), overrides

async def run_agent_stream(db: Session, cleaned_query: str, analysis_profile: Any, profile_overrides: Dict) -> AsyncGenerator[str, None]:
    app_workflow = create_agent_workflow(db)
    
    initial_state = {
        "user_query": cleaned_query,
        "user_profile": analysis_profile,
    }
    
    try:
        # LangGraph allows streaming state updates
        for event in app_workflow.stream(initial_state):
            # Event is a dictionary where key is the node name and value is the output state
            for node_name, state_update in event.items():
                yield f"data: {json.dumps({'type': 'step', 'node': node_name})}\n\n"
                await asyncio.sleep(0.1) # small delay for visual effect on frontend
                
                # Keep track of final state manually or extract from last event
                final_state = state_update
                
        # Format final results
        safe_results = {}
        for scheme_id, res in final_state.get("eligibility_results", {}).items():
            scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
            safe_results[scheme_id] = {
                "scheme": {
                    "id": scheme.id if scheme else scheme_id,
                    "name": scheme.name if scheme else f"Scheme {scheme_id}",
                    "department": scheme.department if scheme else None,
                    "state": scheme.state if scheme else None,
                    "description": scheme.description if scheme else None,
                    "source_url": scheme.source_url if scheme else None,
                },
                "status": res["status"],
                "satisfied_count": len(res["details"]["satisfied"]),
                "failed_count": len(res["details"]["not_satisfied"]),
                "unknown_count": len(res["details"]["unknown"]),
                "verification": res.get("verification", {})
            }
            
        final_payload = {
            "type": "result",
            "data": {
                "query": final_state.get("user_query"),
                "search_keywords": final_state.get("search_keywords"),
                "profile_overrides": profile_overrides,
                "retrieved_chunks_count": len(final_state.get("retrieved_chunks", [])),
                "eligibility_results": safe_results
            }
        }
        
        yield f"data: {json.dumps(final_payload)}\n\n"
        
    except Exception as e:
        print(f"Error in stream: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@router.get("/stream")
async def analyze_stream(
    query: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    cleaned_query = query.strip()
    if not cleaned_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    profile = user_service.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="User profile required.")

    analysis_profile, profile_overrides = _apply_query_overrides(profile, cleaned_query)
    
    return StreamingResponse(
        run_agent_stream(db, cleaned_query, analysis_profile, profile_overrides),
        media_type="text/event-stream"
    )

@router.post("/")
def run_analysis(
    request: AnalyzeRequest,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Run the full LangGraph agentic workflow synchronously."""
    cleaned_query = request.query.strip()
    if not cleaned_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    profile = user_service.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="User profile required.")

    analysis_profile, profile_overrides = _apply_query_overrides(profile, cleaned_query)
        
    app_workflow = create_agent_workflow(db)
    initial_state = {
        "user_query": cleaned_query,
        "user_profile": analysis_profile,
    }
    
    final_state = app_workflow.invoke(initial_state)
    
    safe_results = {}
    for scheme_id, res in final_state.get("eligibility_results", {}).items():
        scheme = db.query(Scheme).filter(Scheme.id == scheme_id).first()
        safe_results[scheme_id] = {
            "scheme": {
                "id": scheme.id if scheme else scheme_id,
                "name": scheme.name if scheme else f"Scheme {scheme_id}",
                "department": scheme.department if scheme else None,
                "state": scheme.state if scheme else None,
                "description": scheme.description if scheme else None,
                "source_url": scheme.source_url if scheme else None,
            },
            "status": res["status"],
            "satisfied_count": len(res["details"]["satisfied"]),
            "failed_count": len(res["details"]["not_satisfied"]),
            "unknown_count": len(res["details"]["unknown"]),
            "verification": res.get("verification", {})
        }
        
    return {
        "query": final_state.get("user_query"),
        "search_keywords": final_state.get("search_keywords"),
        "profile_overrides": profile_overrides,
        "retrieved_chunks_count": len(final_state.get("retrieved_chunks", [])),
        "eligibility_results": safe_results
    }
