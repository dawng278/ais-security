#!/usr/bin/env python3
"""Phase 3 frozen before/after detector evaluation.

The runner writes only to datasets/evidence/phase3/<run_id>/ and does not
mutate Phase 2 manifests, canonical samples, or protected v3 reports.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import subprocess
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets/canonical/phase2_canonical_security_samples.jsonl"
PHASE2_MANIFEST = ROOT / "datasets/manifests/canonical_dataset_manifest.json"
SPLIT_MANIFEST = ROOT / "datasets/manifests/split_manifest.json"
METRIC_VERSION = "phase2_metrics_v1"
FAILURE_TAXONOMY_VERSION = "phase2_failure_taxonomy_v1"
EXPECTED_DATASET_HASH = "a89eb6c09be417209af94f7026e319840195c4239202bec9639242b6a5511549"
EXPECTED_SPLIT_HASH = "51e795858ff2d8460a4eeda9861407853a22bfbe6257dd9fd6bd3da983ef3fce"
PROTECTED_REPORTS = [
    "datasets/reports/v3/benchmark_v3_combined.json",
    "datasets/reports/v3/evidence/evidence_card.md",
    "datasets/reports/v3/evidence/evidence_report.json",
]
EXPECTED_PROTECTED = {
    "datasets/reports/v3/benchmark_v3_combined.json": "863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003",
    "datasets/reports/v3/evidence/evidence_card.md": "c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f",
    "datasets/reports/v3/evidence/evidence_report.json": "c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67",
}


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(canonical_json(row) + "\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def dirty_worktree() -> list[str]:
    return subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).splitlines()


def protected_checksums() -> dict[str, str]:
    return {path: sha256_file(ROOT / path) for path in PROTECTED_REPORTS}


def config_hash() -> str:
    files = [
        "backend/app/firewall/normalizer.py",
        "backend/app/firewall/heuristics.py",
        "backend/app/firewall/obfuscation.py",
        "backend/app/firewall/risk_engine.py",
        "backend/app/firewall/service.py",
        "backend/app/firewall/embedding_detector.py",
        "backend/app/firewall/sanitizer.py",
        "backend/app/grader/mock_grader.py",
    ]
    payload = []
    for rel in files:
        path = ROOT / rel
        payload.append({"path": rel, "sha256": sha256_file(path) if path.exists() else "missing"})
    return sha256_text(canonical_json(payload))


def action_rank(action: str) -> int:
    order = ["allow", "warn", "sanitize", "secure_grade", "manual_review", "block"]
    return order.index(action) if action in order else -1


def safe_div(num: float, den: float, default: float) -> float:
    return default if den == 0 else num / den


def f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall == 0 else 2 * precision * recall / (precision + recall)


def confusion_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    under = over = 0
    for result in results:
        is_attack = result["true_label"] == "attack"
        predicted_attack = result["predicted_label"] == "attack"
        if is_attack and predicted_attack:
            tp += 1
        elif is_attack and not predicted_attack:
            fn += 1
        elif not is_attack and predicted_attack:
            fp += 1
        else:
            tn += 1
        if result["failure_category"] == "under_block":
            under += 1
        if result["failure_category"] == "over_block":
            over += 1
    total = max(len(results), 1)
    attack_precision = safe_div(tp, tp + fp, 1.0)
    attack_recall = safe_div(tp, tp + fn, 1.0)
    clean_precision = safe_div(tn, tn + fn, 1.0)
    clean_recall = safe_div(tn, tn + fp, 1.0)
    return {
        "total_samples": len(results),
        "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "accuracy": round(safe_div(tp + tn, total, 0.0), 4),
        "precision": round(attack_precision, 4),
        "recall": round(attack_recall, 4),
        "macro_f1": round((f1(attack_precision, attack_recall) + f1(clean_precision, clean_recall)) / 2, 4),
        "per_class_f1": {
            "attack": round(f1(attack_precision, attack_recall), 4),
            "clean": round(f1(clean_precision, clean_recall), 4),
        },
        "false_positive_rate": round(safe_div(fp, fp + tn, 0.0), 4),
        "false_negative_rate": round(safe_div(fn, fn + tp, 0.0), 4),
        "failure_count": sum(1 for result in results if result["failure_category"]),
        "under_block_count": under,
        "over_block_count": over,
        "under_block_rate": round(under / total, 4),
        "over_block_rate": round(over / total, 4),
    }


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int(round((pct / 100) * (len(ordered) - 1)))))
    return round(ordered[index], 3)


def evaluate_samples(samples: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    sys.path.insert(0, str(ROOT / "backend"))
    from app.firewall.embedding_detector import get_embedding_detector_health
    from app.firewall.schemas import FirewallAnalyzeRequest
    from app.firewall.service import analyze_submission

    results: list[dict[str, Any]] = []
    latencies: list[float] = []
    for sample in samples:
        task_type = sample["task_type"]
        if task_type in {"generic", "reading"}:
            task_type = "writing"
        start = time.perf_counter()
        response = analyze_submission(FirewallAnalyzeRequest(text=sample["content"], task_type=task_type))
        latency_ms = round((time.perf_counter() - start) * 1000, 3)
        latencies.append(latency_ms)

        selected = response.action
        selected_rank = action_rank(selected)
        expected_ranks = [action_rank(action) for action in sample["expected_action_range"]]
        is_attack = sample["security_label"] == "attack"
        predicted_attack = selected != "allow"
        failure_category = None
        if is_attack and not predicted_attack:
            failure_category = "false_negative"
        elif not is_attack and predicted_attack:
            failure_category = "false_positive"
        if is_attack and selected_rank < min(expected_ranks):
            failure_category = "under_block"
        elif not is_attack and selected_rank > max(expected_ranks):
            failure_category = "over_block"

        results.append(
            {
                "sample_id": sample["sample_id"],
                "track": sample["benchmark_tracks"][0],
                "split": sample["split"],
                "true_label": sample["security_label"],
                "predicted_label": "attack" if predicted_attack else "benign",
                "risk_score": response.risk_score,
                "risk_level": response.risk_level,
                "selected_action": selected,
                "expected_action_range": sample["expected_action_range"],
                "attack_family": sample["attack_family"],
                "language": sample["language"],
                "difficulty": sample["difficulty"],
                "detector_contributions": {
                    "detected_patterns": response.detected_patterns,
                    "normalization_flags": response.normalization_flags,
                    "attack_type": response.attack_type,
                },
                "latency_ms": latency_ms,
                "failure_category": failure_category,
            }
        )

    runtime = {
        "embedding": get_embedding_detector_health(load_model=False),
        "latency_ms": {
            "p50": percentile(latencies, 50),
            "p95": percentile(latencies, 95),
            "p99": percentile(latencies, 99),
            "max": max(latencies) if latencies else 0.0,
        },
    }
    return results, runtime


def aggregate(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_track = {}
    for track in sorted({result["track"] for result in results}):
        track_results = [result for result in results if result["track"] == track]
        metrics = confusion_metrics(track_results)
        metrics["by_attack_family"] = {
            family: confusion_metrics([r for r in track_results if r["attack_family"] == family])
            for family in sorted({r["attack_family"] for r in track_results})
        }
        metrics["by_language"] = {
            language: confusion_metrics([r for r in track_results if r["language"] == language])
            for language in sorted({r["language"] for r in track_results})
        }
        metrics["support_warnings"] = [
            {"dimension": "track", "value": track, "count": len(track_results), "status": "LOW_SUPPORT"}
        ] if len(track_results) < 20 or track == "ielts_domain_security" else []
        by_track[track] = metrics
    return {
        "metric_definitions_version": METRIC_VERSION,
        "tracks": by_track,
        "overall": confusion_metrics(results),
    }


def failure_rows(results: list[dict[str, Any]], *, run_id: str) -> list[dict[str, Any]]:
    rows = []
    for result in results:
        if not result["failure_category"]:
            continue
        rows.append(
            {
                "sample_id": result["sample_id"],
                "track": result["track"],
                "split": result["split"],
                "permitted_split_visibility": "aggregate_only" if result["split"] == "private_holdout" else "sample_id_only",
                "true_label": result["true_label"],
                "predicted_label": result["predicted_label"],
                "risk_score": result["risk_score"],
                "selected_action": result["selected_action"],
                "expected_action_range": result["expected_action_range"],
                "detector_contributions": result["detector_contributions"],
                "attack_family": result["attack_family"],
                "language": result["language"],
                "difficulty": result["difficulty"],
                "root_cause_category": result["failure_category"],
                "proposed_general_fix": "general detector/policy improvement; no exact sample memorization",
                "overfitting_risk": "private_holdout_content_not_exported" if result["split"] == "private_holdout" else "low",
                "run_id": run_id,
            }
        )
    return rows


def compare(before_dir: Path, after_results: list[dict[str, Any]]) -> dict[str, Any]:
    before = {row["sample_id"]: row for row in read_jsonl(before_dir / "predictions.jsonl")}
    changed = []
    summary = Counter()
    for after in after_results:
        old = before.get(after["sample_id"])
        if not old:
            continue
        if old["selected_action"] == after["selected_action"] and old["predicted_label"] == after["predicted_label"]:
            continue
        old_failure = old.get("failure_category")
        new_failure = after.get("failure_category")
        if old_failure and not new_failure:
            category = "corrected_failure"
        elif not old_failure and new_failure:
            category = "new_failure"
        elif old_failure and new_failure:
            category = "changed_failure"
        else:
            category = "action_changed_no_failure"
        summary[category] += 1
        changed.append(
            {
                "sample_id": after["sample_id"],
                "track": after["track"],
                "split": after["split"],
                "attack_family": after["attack_family"],
                "old_action": old["selected_action"],
                "new_action": after["selected_action"],
                "old_failure": old_failure,
                "new_failure": new_failure,
                "change_category": category,
            }
        )
    return {
        "changed_predictions": changed,
        "summary": dict(sorted(summary.items())),
    }


def environment() -> dict[str, Any]:
    return {
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "network_required": False,
    }


def checksum_manifest(directory: Path) -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): sha256_file(path)
        for path in sorted(directory.rglob("*"))
        if path.is_file() and path.name not in {"checksum_manifest.txt"}
    }


def write_checksum_txt(path: Path, checksums: dict[str, str]) -> None:
    path.write_text("".join(f"{digest}  {file}\n" for file, digest in sorted(checksums.items())), encoding="utf-8")


def evidence_card(run_id: str, metrics: dict[str, Any], comparison: dict[str, Any] | None) -> str:
    generic = metrics["tracks"].get("generic_prompt_injection", {})
    ielts = metrics["tracks"].get("ielts_domain_security", {})
    lines = [
        "# Phase 3 Evidence Card",
        "",
        f"Run ID: `{run_id}`",
        "",
        "## Generic Prompt Injection",
        "",
        f"- Samples: {generic.get('total_samples')}",
        f"- Accuracy: {generic.get('accuracy')}",
        f"- Recall: {generic.get('recall')}",
        f"- Failures: {generic.get('failure_count')}",
        f"- Under-block: {generic.get('under_block_count')}",
        "",
        "## IELTS Domain Security",
        "",
        f"- Samples: {ielts.get('total_samples')}",
        f"- Accuracy: {ielts.get('accuracy')}",
        f"- Recall: {ielts.get('recall')}",
        "- Support: LOW_SUPPORT",
        "",
        "## Comparison",
        "",
    ]
    if comparison:
        lines.append(f"- Changed predictions: {len(comparison['changed_predictions'])}")
        lines.append(f"- Summary: `{comparison['summary']}`")
    else:
        lines.append("- Prechange baseline; no comparison yet.")
    lines.extend([
        "",
        "## Truth labels",
        "",
        "- Embedding unavailable/degraded unless detector health proves otherwise.",
        "- Score integrity remains DETERMINISTIC_DEMO / NOT_MEASURED.",
        "- No protected v3 report is included.",
    ])
    return "\n".join(lines) + "\n"


def run(run_id: str, baseline_dir: Path | None = None, approved: bool = False) -> dict[str, Any]:
    dataset_manifest = read_json(PHASE2_MANIFEST)
    split_manifest = read_json(SPLIT_MANIFEST)
    if dataset_manifest["dataset_hash"] != EXPECTED_DATASET_HASH:
        raise SystemExit("Frozen dataset hash mismatch")
    if split_manifest["split_hash"] != EXPECTED_SPLIT_HASH:
        raise SystemExit("Frozen split hash mismatch")
    protected = protected_checksums()
    if protected != EXPECTED_PROTECTED:
        raise SystemExit("Protected report checksum mismatch")

    samples = read_jsonl(DATASET_PATH)
    results, runtime = evaluate_samples(samples)
    metrics = aggregate(results)
    comparison = compare(baseline_dir, results) if baseline_dir else None
    output = ROOT / "datasets/evidence/phase3" / run_id
    output.mkdir(parents=True, exist_ok=True)

    run_manifest = {
        "schema_version": "phase3_evidence_bundle.v1",
        "run_id": run_id,
        "status": "approved" if approved else "generated",
        "review_state": "approved" if approved else "generated",
        "git_commit": git_commit(),
        "dirty_worktree": dirty_worktree(),
        "dataset_hash": dataset_manifest["dataset_hash"],
        "split_hash": split_manifest["split_hash"],
        "detector_config_hash": config_hash(),
        "policy_config_hash": config_hash(),
        "threshold_calibration_version": "phase3_static_weighted_v1",
        "detector_health": runtime["embedding"],
        "environment": environment(),
        "metric_definitions_version": METRIC_VERSION,
        "failure_taxonomy_version": FAILURE_TAXONOMY_VERSION,
        "protected_report_checksums": protected,
        "phase2_evidence_bundle_hash": read_json(ROOT / "datasets/manifests/approved_evidence_run.json")["bundle_hash"],
        "limitations": [
            "Private holdout content is not exported.",
            "IELTS-domain track is LOW_SUPPORT.",
            "Measured score-integrity remains NOT_MEASURED.",
        ],
    }
    write_json(output / "run_manifest.json", run_manifest)
    write_json(output / "metrics.json", metrics)
    write_json(output / "confusion_matrix.json", {track: data["confusion_matrix"] for track, data in metrics["tracks"].items()})
    write_jsonl(output / "predictions.jsonl", results)
    write_jsonl(output / "failure_analysis.jsonl", failure_rows(results, run_id=run_id))
    write_json(output / "detector_health.json", runtime["embedding"])
    write_json(output / "detector_contributions_summary.json", {
        "patterns": dict(sorted(Counter(pattern for row in results for pattern in row["detector_contributions"]["detected_patterns"]).items())),
        "normalization_flags": dict(sorted(Counter(flag for row in results for flag in row["detector_contributions"]["normalization_flags"]).items())),
    })
    write_json(output / "policy_action_summary.json", dict(sorted(Counter(row["selected_action"] for row in results).items())))
    write_json(output / "calibration_report.json", {
        "version": "phase3_static_weighted_v1",
        "method": "static deterministic weighted mapping",
        "calibration_data": "train/development only; no private holdout tuning",
        "limitations": "risk_score is a calibrated risk indicator, not probability",
    })
    write_json(output / "latency_report.json", runtime["latency_ms"])
    write_json(output / "environment.json", environment())
    write_json(output / "dataset_manifest.json", dataset_manifest)
    write_json(output / "config_manifest.json", {
        "detector_config_hash": run_manifest["detector_config_hash"],
        "policy_config_hash": run_manifest["policy_config_hash"],
        "threshold_calibration_version": run_manifest["threshold_calibration_version"],
    })
    if comparison:
        write_json(output / "metrics_comparison.json", {"summary": comparison["summary"]})
        write_jsonl(output / "changed_predictions.jsonl", comparison["changed_predictions"])
    else:
        write_json(output / "metrics_comparison.json", {"summary": "prechange_baseline_no_comparison"})
        write_jsonl(output / "changed_predictions.jsonl", [])
    (output / "evidence_card.md").write_text(evidence_card(run_id, metrics, comparison), encoding="utf-8")
    (output / "limitations.md").write_text(
        "# Limitations\n\n- IELTS metrics are LOW_SUPPORT.\n- Embedding availability depends on optional dependencies.\n- Score integrity is not measured in Phase 3.\n- Local latency is not production capacity.\n",
        encoding="utf-8",
    )
    write_checksum_txt(output / "checksum_manifest.txt", checksum_manifest(output))
    return {
        "run_id": run_id,
        "output_dir": str(output.relative_to(ROOT)),
        "metrics": metrics,
        "comparison": comparison,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--baseline-dir")
    parser.add_argument("--approved", action="store_true")
    args = parser.parse_args()
    baseline_dir = Path(args.baseline_dir) if args.baseline_dir else None
    if baseline_dir and not baseline_dir.is_absolute():
        baseline_dir = ROOT / baseline_dir
    result = run(args.run_id, baseline_dir=baseline_dir, approved=args.approved)
    print(json.dumps({
        "run_id": result["run_id"],
        "output_dir": result["output_dir"],
        "generic": result["metrics"]["tracks"].get("generic_prompt_injection"),
        "ielts": result["metrics"]["tracks"].get("ielts_domain_security"),
        "comparison": result["comparison"]["summary"] if result["comparison"] else None,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
