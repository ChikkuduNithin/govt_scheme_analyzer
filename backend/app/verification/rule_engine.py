from enum import Enum
from typing import Dict, Any, List
from datetime import date
from app.models.user import UserProfile
from app.models.eligibility import EligibilityRule

class RuleStatus(str, Enum):
    SATISFIED = "SATISFIED"
    NOT_SATISFIED = "NOT_SATISFIED"
    UNKNOWN = "UNKNOWN"

class SchemeEligibilityStatus(str, Enum):
    LIKELY_ELIGIBLE = "LIKELY_ELIGIBLE"
    POSSIBLY_ELIGIBLE = "POSSIBLY_ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    INSUFFICIENT_INFORMATION = "INSUFFICIENT_INFORMATION"

def calculate_age(dob: date) -> int:
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

def extract_user_field(profile: UserProfile, field: str) -> Any:
    if field == "age":
        if profile.date_of_birth:
            return calculate_age(profile.date_of_birth)
        return None
    return getattr(profile, field, None)

def evaluate_condition(user_val: Any, operator: str, rule_val: Any) -> bool:
    if operator == "==":
        return user_val == rule_val
    elif operator == "!=":
        return user_val != rule_val
    elif operator == ">=":
        return float(user_val) >= float(rule_val)
    elif operator == "<=":
        return float(user_val) <= float(rule_val)
    elif operator == ">":
        return float(user_val) > float(rule_val)
    elif operator == "<":
        return float(user_val) < float(rule_val)
    elif operator == "IN":
        if isinstance(rule_val, list):
            return user_val in rule_val
        return user_val in str(rule_val).split(",")
    return False

def evaluate_rule(profile: UserProfile, rule: EligibilityRule) -> RuleStatus:
    condition = rule.condition
    if not isinstance(condition, dict) or "field" not in condition or "operator" not in condition or "value" not in condition:
        return RuleStatus.UNKNOWN
        
    user_val = extract_user_field(profile, condition["field"])
    if user_val is None:
        return RuleStatus.UNKNOWN
        
    try:
        is_met = evaluate_condition(user_val, condition["operator"], condition["value"])
        return RuleStatus.SATISFIED if is_met else RuleStatus.NOT_SATISFIED
    except (ValueError, TypeError):
        return RuleStatus.UNKNOWN

def evaluate_scheme_eligibility(profile: UserProfile, rules: List[EligibilityRule]) -> Dict:
    results = {
        "satisfied": [],
        "not_satisfied": [],
        "unknown": []
    }
    
    if not rules:
        return {
            "status": SchemeEligibilityStatus.INSUFFICIENT_INFORMATION,
            "details": results
        }
        
    for rule in rules:
        status = evaluate_rule(profile, rule)
        if status == RuleStatus.SATISFIED:
            results["satisfied"].append(rule)
        elif status == RuleStatus.NOT_SATISFIED:
            results["not_satisfied"].append(rule)
        else:
            results["unknown"].append(rule)
            
    if results["not_satisfied"]:
        final_status = SchemeEligibilityStatus.NOT_ELIGIBLE
    elif results["unknown"]:
        if results["satisfied"]:
            final_status = SchemeEligibilityStatus.POSSIBLY_ELIGIBLE
        else:
            final_status = SchemeEligibilityStatus.INSUFFICIENT_INFORMATION
    else:
        final_status = SchemeEligibilityStatus.LIKELY_ELIGIBLE
        
    return {
        "status": final_status,
        "details": results
    }
