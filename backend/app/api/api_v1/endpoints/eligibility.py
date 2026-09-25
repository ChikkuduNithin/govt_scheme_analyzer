from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.models.user import User
from app.models.eligibility import EligibilityRule
from app.services import scheme_service, user_service
from app.schemas.eligibility import EligibilityResponse, RuleDetail
from app.verification.rule_engine import evaluate_scheme_eligibility

router = APIRouter()

@router.post("/check/{scheme_id}", response_model=EligibilityResponse)
def check_eligibility(
    scheme_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """Check eligibility for a scheme using deterministic rule engine."""
    # 1. Get Scheme and Rules
    scheme = scheme_service.get_scheme(db, scheme_id)
    rules = db.query(EligibilityRule).filter(EligibilityRule.scheme_id == scheme.id).all()
    
    # 2. Get User Profile
    profile = user_service.get_user_profile(db, current_user.id)
    if not profile:
        raise HTTPException(status_code=400, detail="User profile not found. Please complete profile.")
        
    # 3. Evaluate rules
    result = evaluate_scheme_eligibility(profile, rules)
    
    # 4. Format response
    def format_rules(rule_list):
        return [RuleDetail(rule_id=r.id, rule_type=r.rule_type, description=r.description) for r in rule_list]
        
    return EligibilityResponse(
        scheme_id=scheme_id,
        status=result["status"],
        satisfied_criteria=format_rules(result["details"]["satisfied"]),
        failed_criteria=format_rules(result["details"]["not_satisfied"]),
        unknown_criteria=format_rules(result["details"]["unknown"])
    )
