import json
import unittest
from app.benchmark.case_library import ScenarioCase
from app.benchmark.case_library_runner import load_case_library, evaluate_case_library, evaluate_single_case
from app.benchmark.decision_matrix import get_decision_matrix


class TestCaseLibrary(unittest.TestCase):
    def test_case_library_loads(self):
        cases = load_case_library()
        self.assertGreaterEqual(len(cases), 60)
        self.assertIsInstance(cases[0], ScenarioCase)

    def test_decision_matrix_contains_required_conditions(self):
        matrix = get_decision_matrix()
        self.assertGreaterEqual(len(matrix), 5)
        conditions = [item["condition"].lower() for item in matrix]
        self.assertTrue(any("direct score manipulation" in c for c in conditions))
        self.assertTrue(any("role spoofing" in c for c in conditions))
        self.assertTrue(any("academic discussion" in c for c in conditions))

    def test_vietnamese_score_case_expected_secure_grade(self):
        cases = load_case_library()
        vi_case = next((c for c in cases if c.case_id == "case_multi_001"), None)
        self.assertIsNotNone(vi_case)
        if vi_case:
            res = evaluate_single_case(vi_case)
            self.assertTrue(res.passed)
            self.assertIn(res.predicted_action, ["secure_grade", "manual_review"])

    def test_benign_prompt_injection_discussion_expected_allow_or_warn(self):
        cases = load_case_library()
        academic_case = next((c for c in cases if c.case_id == "case_clean_005"), None)
        self.assertIsNotNone(academic_case)
        if academic_case:
            res = evaluate_single_case(academic_case)
            self.assertTrue(res.passed)
            self.assertIn(res.predicted_action, ["allow", "warn"])

    def test_case_library_report_json_serializable(self):
        report = evaluate_case_library()
        self.assertGreaterEqual(report.total_cases, 60)
        self.assertGreater(report.pass_rate, 0.5)
        
        # Test serialization
        report_dict = report.model_dump()
        dumped_str = json.dumps(report_dict)
        self.assertIn("total_cases", dumped_str)
        self.assertIn("pass_rate", dumped_str)


if __name__ == "__main__":
    unittest.main()
