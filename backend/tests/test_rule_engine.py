from datetime import date
from app.models.user import UserProfile
from app.models.eligibility import EligibilityRule
from app.verification.rule_engine import evaluate_rule, RuleStatus, evaluate_scheme_eligibility

def test_evaluate_rule_age_satisfied():
    profile = UserProfile(date_of_birth=date(2000, 1, 1)) # Age 26 (in 2026)
    rule = EligibilityRule(
        rule_type="age",
        condition={"field": "age", "operator": ">=", "value": 18},
        description="Must be at least 18 years old"
    )
    status = evaluate_rule(profile, rule)
    assert status == RuleStatus.SATISFIED

def test_evaluate_rule_age_not_satisfied():
    profile = UserProfile(date_of_birth=date(2010, 1, 1)) # Age 16
    rule = EligibilityRule(
        rule_type="age",
        condition={"field": "age", "operator": ">=", "value": 18},
        description="Must be at least 18 years old"
    )
    status = evaluate_rule(profile, rule)
    assert status == RuleStatus.NOT_SATISFIED

def test_evaluate_rule_missing_profile_field():
    profile = UserProfile() # No DOB
    rule = EligibilityRule(
        rule_type="age",
        condition={"field": "age", "operator": ">=", "value": 18},
        description="Must be at least 18 years old"
    )
    status = evaluate_rule(profile, rule)
    assert status == RuleStatus.UNKNOWN
