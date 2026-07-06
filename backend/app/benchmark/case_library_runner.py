import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.benchmark.case_library import ScenarioCase
from app.firewall.schemas import FirewallAnalyzeRequest
from app.firewall.service import analyze_submission


class CaseLibraryEvaluationResult(BaseModel):
    case_id: str
    title: str
    scenario_group: str
    language: str
    task_type: str
    primary_perspective: str
    expected_action: str
    predicted_action: str
    risk_score: float
    passed: bool
    failure_reason: Optional[str] = None
    under_block_risk: str
    over_block_risk: str
    stakeholder_lenses: List[str] = Field(default_factory=list)
    evidence_observed: Dict[str, Any] = Field(default_factory=dict)
    text_preview: str = ""


class CaseLibraryEvaluationReport(BaseModel):
    total_cases: int
    passed_cases: int
    failed_cases: int
    pass_rate: float
    by_perspective: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_scenario_group: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_language: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    by_expected_action: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    most_fragile_perspective: str = "security"
    strongest_perspective: str = "fairness"
    is_demo: bool = False
    results: List[CaseLibraryEvaluationResult] = Field(default_factory=list)


def resolve_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "frontend").exists() or (current / "PROJECT_CONTEXT_FOR_REVIEW.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent


def load_case_library(path: Optional[str] = None) -> List[ScenarioCase]:
    root = resolve_project_root()
    if path:
        file_path = Path(path)
    else:
        file_path = root / "datasets" / "scenarios" / "gradingguard_case_library.jsonl"

    if not file_path.exists():
        return []

    cases: List[ScenarioCase] = []
    with file_path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                data = json.loads(line)
                cases.append(ScenarioCase(**data))
    return cases


def evaluate_single_case(sc_case: ScenarioCase) -> CaseLibraryEvaluationResult:
    req = FirewallAnalyzeRequest(
        text=sc_case.text,
        task_type=sc_case.task_type,
        domain="ielts",
        language=sc_case.language,
    )
    res = analyze_submission(req)

    predicted_action = res.action
    risk_score = res.risk_score
    expected_action = sc_case.expected_action

    passed = False
    failure_reason = None

    if expected_action == "allow":
        if predicted_action in ["allow", "warn"]:
            passed = True
        else:
            failure_reason = f"Over-blocked benign case. Expected allow/warn, got {predicted_action}"
    elif expected_action == "warn":
        if sc_case.is_attack:
            if predicted_action in ["warn", "secure_grade", "manual_review"]:
                passed = True
            else:
                failure_reason = f"Under-blocked indirect attack. Expected warn/secure_grade/manual_review, got {predicted_action}"
        else:
            if predicted_action in ["allow", "warn"]:
                passed = True
            else:
                failure_reason = f"Expected allow/warn, got {predicted_action}"
    elif expected_action == "secure_grade":
        if predicted_action in ["secure_grade", "manual_review"]:
            passed = True
        else:
            failure_reason = f"Under-blocked attack payload. Expected secure_grade/manual_review, got {predicted_action}"
    elif expected_action == "manual_review":
        if predicted_action in ["manual_review", "secure_grade", "warn"]:
            passed = True
        else:
            failure_reason = f"Failed to escalate high-risk or ambiguous case. Expected manual_review/secure_grade/warn, got {predicted_action}"
    else:
        passed = (predicted_action == expected_action)
        if not passed:
            failure_reason = f"Action mismatch. Expected {expected_action}, got {predicted_action}"

    evidence = {
        "risk_score": risk_score,
        "attack_type": res.attack_type,
        "patterns_count": len(res.detected_patterns),
        "obfuscation_detected": len(res.normalization_flags) > 0,
    }

    return CaseLibraryEvaluationResult(
        case_id=sc_case.case_id,
        title=sc_case.title,
        scenario_group=sc_case.scenario_group,
        language=sc_case.language,
        task_type=sc_case.task_type,
        primary_perspective=sc_case.primary_perspective,
        expected_action=expected_action,
        predicted_action=predicted_action,
        risk_score=risk_score,
        passed=passed,
        failure_reason=failure_reason,
        under_block_risk=sc_case.decision_rationale.under_block_risk,
        over_block_risk=sc_case.decision_rationale.over_block_risk,
        stakeholder_lenses=sc_case.stakeholder_lenses,
        evidence_observed=evidence,
        text_preview=sc_case.text[:100],
    )


def evaluate_case_library(path: Optional[str] = None) -> CaseLibraryEvaluationReport:
    cases = load_case_library(path)
    results: List[CaseLibraryEvaluationResult] = []

    for c in cases:
        results.append(evaluate_single_case(c))

    total = len(results)
    passed_cnt = sum(1 for r in results if r.passed)
    failed_cnt = total - passed_cnt
    pass_rate = round(passed_cnt / max(total, 1), 3)

    by_perspective: Dict[str, Dict[str, Any]] = {}
    by_group: Dict[str, Dict[str, Any]] = {}
    by_lang: Dict[str, Dict[str, Any]] = {}
    by_action: Dict[str, Dict[str, Any]] = {}

    for r in results:
        p = r.primary_perspective
        if p not in by_perspective:
            by_perspective[p] = {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
        by_perspective[p]["total"] += 1
        if r.passed:
            by_perspective[p]["passed"] += 1
        else:
            by_perspective[p]["failed"] += 1

        sg = r.scenario_group
        if sg not in by_group:
            by_group[sg] = {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
        by_group[sg]["total"] += 1
        if r.passed:
            by_group[sg]["passed"] += 1
        else:
            by_group[sg]["failed"] += 1

        l = r.language
        if l not in by_lang:
            by_lang[l] = {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
        by_lang[l]["total"] += 1
        if r.passed:
            by_lang[l]["passed"] += 1
        else:
            by_lang[l]["failed"] += 1

        act = r.expected_action
        if act not in by_action:
            by_action[act] = {"total": 0, "passed": 0, "failed": 0, "pass_rate": 0.0}
        by_action[act]["total"] += 1
        if r.passed:
            by_action[act]["passed"] += 1
        else:
            by_action[act]["failed"] += 1

    for d in [by_perspective, by_group, by_lang, by_action]:
        for k, v in d.items():
            v["pass_rate"] = round(v["passed"] / max(v["total"], 1), 3)

    sorted_p = sorted(by_perspective.items(), key=lambda x: x[1]["pass_rate"])
    most_fragile = sorted_p[0][0] if sorted_p else "security"
    strongest = sorted_p[-1][0] if sorted_p else "fairness"

    report = CaseLibraryEvaluationReport(
        total_cases=total,
        passed_cases=passed_cnt,
        failed_cases=failed_cnt,
        pass_rate=pass_rate,
        by_perspective=by_perspective,
        by_scenario_group=by_group,
        by_language=by_lang,
        by_expected_action=by_action,
        most_fragile_perspective=most_fragile,
        strongest_perspective=strongest,
        is_demo=False,
        results=results,
    )

    root = resolve_project_root()
    reports_dir = root / "datasets" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    with (reports_dir / "case_library_report.json").open("w", encoding="utf-8") as f:
        json.dump(report.model_dump(), f, indent=2, ensure_ascii=False)

    with (reports_dir / "case_library_results.jsonl").open("w", encoding="utf-8") as f:
        for res in results:
            f.write(json.dumps(res.model_dump(), ensure_ascii=False) + "\n")

    return report


if __name__ == "__main__":
    rep = evaluate_case_library()
    print(f"Case library total: {rep.total_cases}")
    print(f"Case library pass rate: {rep.pass_rate * 100:.1f}%")
    print(f"Strongest perspective: {rep.strongest_perspective}")
    print(f"Weakest perspective: {rep.most_fragile_perspective}")
