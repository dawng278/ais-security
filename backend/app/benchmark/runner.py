from pydantic import BaseModel
from app.firewall.service import analyze_submission
from app.firewall.schemas import FirewallAnalyzeRequest


class BenchmarkCase(BaseModel):
    id: str
    task_type: str = "writing"
    label: str
    text: str
    expected_action: str


class BenchmarkCaseResult(BaseModel):
    id: str
    label: str
    expected_action: str
    actual_action: str
    risk_score: float
    passed: bool


class BenchmarkSummary(BaseModel):
    total_cases: int
    passed_cases: int
    accuracy: float
    precision: float
    recall: float
    false_positive_rate: float
    case_results: list[BenchmarkCaseResult]


def run_benchmark(cases: list[BenchmarkCase]) -> BenchmarkSummary:
    results: list[BenchmarkCaseResult] = []
    tp = fp = tn = fn = 0

    for case in cases:
        req = FirewallAnalyzeRequest(text=case.text, task_type=case.task_type)
        res = analyze_submission(req)
        
        is_attack = case.expected_action != "allow"
        predicted_attack = res.action != "allow"
        passed = (case.expected_action == res.action) or (is_attack == predicted_attack)

        if is_attack and predicted_attack:
            tp += 1
        elif not is_attack and predicted_attack:
            fp += 1
        elif not is_attack and not predicted_attack:
            tn += 1
        elif is_attack and not predicted_attack:
            fn += 1

        results.append(
            BenchmarkCaseResult(
                id=case.id,
                label=case.label,
                expected_action=case.expected_action,
                actual_action=res.action,
                risk_score=res.risk_score,
                passed=passed,
            )
        )

    total = len(cases)
    passed_cnt = sum(1 for r in results if r.passed)
    precision = round(tp / (tp + fp), 2) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 2) if (tp + fn) > 0 else 1.0
    fpr = round(fp / (fp + tn), 2) if (fp + tn) > 0 else 0.0

    return BenchmarkSummary(
        total_cases=total,
        passed_cases=passed_cnt,
        accuracy=round(passed_cnt / total, 2) if total > 0 else 0.0,
        precision=precision,
        recall=recall,
        false_positive_rate=fpr,
        case_results=results,
    )
