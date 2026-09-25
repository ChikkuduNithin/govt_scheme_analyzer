from pydantic import BaseModel
from typing import List, Dict, Any
from app.verification.rule_engine import SchemeEligibilityStatus

class RuleDetail(BaseModel):
    rule_id: int
    rule_type: str
    description: str

class EligibilityResponse(BaseModel):
    scheme_id: int
    status: SchemeEligibilityStatus
    satisfied_criteria: List[RuleDetail]
    failed_criteria: List[RuleDetail]
    unknown_criteria: List[RuleDetail]
