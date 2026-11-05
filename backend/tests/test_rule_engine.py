import unittest
from datetime import date
from app.models.user import UserProfile
from app.models.eligibility import EligibilityRule
from app.verification.rule_engine import (
    evaluate_rule, 
    RuleStatus, 
    evaluate_scheme_eligibility, 
    SchemeEligibilityStatus,
    calculate_age
)

class TestRuleEngine(unittest.TestCase):
    def test_calculate_age(self):
        # Calculate age dynamically based on current date
        today = date.today()
        dob_20 = date(today.year - 20, today.month, today.day)
        self.assertEqual(calculate_age(dob_20), 20)

    def test_evaluate_rule_age_satisfied(self):
        today = date.today()
        profile = UserProfile(date_of_birth=date(today.year - 25, today.month, today.day))
        rule = EligibilityRule(
            rule_type="age",
            condition={"field": "age", "operator": ">=", "value": 18},
            description="Must be at least 18 years old"
        )
        status = evaluate_rule(profile, rule)
        self.assertEqual(status, RuleStatus.SATISFIED)

    def test_evaluate_rule_age_not_satisfied(self):
        today = date.today()
        profile = UserProfile(date_of_birth=date(today.year - 16, today.month, today.day))
        rule = EligibilityRule(
            rule_type="age",
            condition={"field": "age", "operator": ">=", "value": 18},
            description="Must be at least 18 years old"
        )
        status = evaluate_rule(profile, rule)
        self.assertEqual(status, RuleStatus.NOT_SATISFIED)

    def test_evaluate_rule_income(self):
        profile = UserProfile(annual_income=180000.0)
        rule_pass = EligibilityRule(
            rule_type="income",
            condition={"field": "annual_income", "operator": "<=", "value": 250000},
            description="Income <= 2.5 Lakhs"
        )
        rule_fail = EligibilityRule(
            rule_type="income",
            condition={"field": "annual_income", "operator": "<=", "value": 150000},
            description="Income <= 1.5 Lakhs"
        )
        self.assertEqual(evaluate_rule(profile, rule_pass), RuleStatus.SATISFIED)
        self.assertEqual(evaluate_rule(profile, rule_fail), RuleStatus.NOT_SATISFIED)

    def test_evaluate_rule_category_in(self):
        profile = UserProfile(category="OBC")
        rule = EligibilityRule(
            rule_type="category",
            condition={"field": "category", "operator": "IN", "value": ["SC", "ST", "OBC"]},
            description="Must belong to SC/ST/OBC"
        )
        self.assertEqual(evaluate_rule(profile, rule), RuleStatus.SATISFIED)

        profile_general = UserProfile(category="General")
        self.assertEqual(evaluate_rule(profile_general, rule), RuleStatus.NOT_SATISFIED)

    def test_evaluate_scheme_overall_status(self):
        today = date.today()
        profile = UserProfile(
            date_of_birth=date(today.year - 22, today.month, today.day),
            annual_income=150000.0,
            category="OBC",
            state="Telangana"
        )
        rules = [
            EligibilityRule(condition={"field": "annual_income", "operator": "<=", "value": 250000}, description="Income limit"),
            EligibilityRule(condition={"field": "category", "operator": "IN", "value": ["SC", "ST", "OBC"]}, description="Category"),
            EligibilityRule(condition={"field": "state", "operator": "==", "value": "Telangana"}, description="State")
        ]
        result = evaluate_scheme_eligibility(profile, rules)
        self.assertEqual(result["status"], SchemeEligibilityStatus.LIKELY_ELIGIBLE)
        self.assertEqual(len(result["details"]["satisfied"]), 3)
        self.assertEqual(len(result["details"]["not_satisfied"]), 0)

if __name__ == "__main__":
    unittest.main()
