from typing import List
from app.benchmark.schemas import (
    BenchmarkSample,
    BenchmarkReportV2,
    BenchmarkCaseEvaluationResult,
)
from app.firewall.service import analyze_submission
from app.firewall.schemas import FirewallAnalyzeRequest


def run_benchmark_v2(samples: List[BenchmarkSample]) -> BenchmarkReportV2:
    evaluations: List[BenchmarkCaseEvaluationResult] = []
    tp = fp = tn = fn = 0
    over_block = under_block = 0

    attack_counts: dict[str, dict[str, int]] = {}
    lang_counts: dict[str, dict[str, int]] = {}

    for sample in samples:
        req = FirewallAnalyzeRequest(text=sample.text, task_type=sample.task_type)
        res = analyze_submission(req)

        is_attack = sample.expected_action != "allow"
        predicted_attack = res.action != "allow"

        passed = (sample.expected_action == res.action) or (is_attack == predicted_attack)

        error_type = None
        if not passed:
            if not is_attack and predicted_attack:
                error_type = "false_positive"
                over_block += 1
            elif is_attack and not predicted_attack:
                error_type = "under_block"
                under_block += 1

        if is_attack and predicted_attack:
            tp += 1
        elif not is_attack and predicted_attack:
            fp += 1
        elif not is_attack and not predicted_attack:
            tn += 1
        elif is_attack and not predicted_attack:
            fn += 1

        # Track by attack type
        atk = sample.attack_type
        if atk not in attack_counts:
            attack_counts[atk] = {"total": 0, "passed": 0}
        attack_counts[atk]["total"] += 1
        if passed:
            attack_counts[atk]["passed"] += 1

        # Track by language
        lang = sample.language
        if lang not in lang_counts:
            lang_counts[lang] = {"total": 0, "passed": 0}
        lang_counts[lang]["total"] += 1
        if passed:
            lang_counts[lang]["passed"] += 1

        evaluations.append(
            BenchmarkCaseEvaluationResult(
                sample_id=sample.id,
                group_id=sample.group_id,
                label=sample.label,
                attack_type=sample.attack_type,
                expected_action=sample.expected_action,
                predicted_action=res.action,
                risk_score=res.risk_score,
                passed=passed,
                error_type=error_type,
                language=sample.language,
                text_preview=sample.text[:120] + ("..." if len(sample.text) > 120 else ""),
            )
        )

    total = len(samples)
    passed_cases = sum(1 for e in evaluations if e.passed)
    precision = round(tp / (tp + fp), 2) if (tp + fp) > 0 else 1.0
    recall = round(tp / (tp + fn), 2) if (tp + fn) > 0 else 1.0
    macro_f1 = round(2 * (precision * recall) / (precision + recall), 2) if (precision + recall) > 0 else 0.0
    fpr = round(fp / (fp + tn), 2) if (fp + tn) > 0 else 0.0
    under_block_rate = round(under_block / total, 2) if total > 0 else 0.0
    over_block_rate = round(over_block / total, 2) if total > 0 else 0.0

    by_attack_type = {
        k: {
            "accuracy": round(v["passed"] / v["total"], 2) if v["total"] > 0 else 0.0,
            "total": v["total"],
        }
        for k, v in attack_counts.items()
    }

    by_language = {
        k: {
            "accuracy": round(v["passed"] / v["total"], 2) if v["total"] > 0 else 0.0,
            "total": v["total"],
        }
        for k, v in lang_counts.items()
    }

    failures = [e for e in evaluations if not e.passed]

    return BenchmarkReportV2(
        benchmark_id="gg_benchmark_v2",
        total_cases=total,
        passed_cases=passed_cases,
        accuracy=round(passed_cases / total, 2) if total > 0 else 0.0,
        precision=precision,
        recall=recall,
        macro_f1=macro_f1,
        false_positive_rate=fpr,
        under_block_rate=under_block_rate,
        over_block_rate=over_block_rate,
        by_attack_type=by_attack_type,
        by_language=by_language,
        failure_cases=failures,
    )
