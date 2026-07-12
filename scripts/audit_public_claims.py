#!/usr/bin/env python3
"""Read-only public claim drift audit for Phase 0."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


DEFAULT_SCAN_PATHS = [
    "README.md",
    "docs/technical_report.md",
    "docs/evaluation_report.md",
    "docs/judge_qna.md",
    "docs/demo_script.md",
    "docs/demo_script_5min.md",
    "docs/demo_script_top1.md",
    "docs/final_submission_checklist.md",
    "docs/final_slide_deck_content.md",
    "docs/final_one_pager.md",
    "docs/pitch_deck_outline.md",
    "docs/presentation_deck_outline.md",
    "docs/verification_report.md",
    "frontend/src/app/benchmark/page.tsx",
    "frontend/src/app/dashboard/page.tsx",
    "frontend/src/app/evidence/page.tsx",
    "frontend/src/app/judge-view/page.tsx",
    "frontend/src/components/AppShell.tsx",
]

REQUIRED_FRONTEND_ROUTES = {
    "/",
    "/attack-arena",
    "/benchmark",
    "/dashboard",
    "/data-lineage",
    "/evidence",
    "/judge-view",
    "/playground",
}

ALLOWED_CONTEXT = re.compile(
    r"not currently|not measured|unavailable|historical|previous|older|downgraded|unverified|future work|target|planned|example",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ClaimPattern:
    claim_type: str
    pattern: re.Pattern[str]
    message: str


CLAIM_PATTERNS = [
    ClaimPattern(
        "stale_macro_f1",
        re.compile(r"(Macro F1[^\n]*(?:0\.90|90%)|(?:0\.90|90%)[^\n]*Macro F1)", re.IGNORECASE),
        "Macro F1 must use current measured value 0.64 or be explicitly historical/planned.",
    ),
    ClaimPattern(
        "stale_recall",
        re.compile(r"(Recall[^\n]*0\.91|0\.91[^\n]*Recall)", re.IGNORECASE),
        "Recall must use current measured value 0.47 or be explicitly historical/planned.",
    ),
    ClaimPattern(
        "stale_fpr",
        re.compile(r"(FPR|False Positive Rate)[^\n]*0\.06", re.IGNORECASE),
        "FPR must use current measured value 0.00 or be explicitly historical/planned.",
    ),
    ClaimPattern(
        "stale_latency",
        re.compile(r"p95[^\n]*(?:210\s*ms|210ms)", re.IGNORECASE),
        "p95 210ms is not current measured production latency evidence.",
    ),
    ClaimPattern(
        "stale_attack_count",
        re.compile(r"(?:3,000|3000(?!/))[^\n]*(?:attack|injection|variant)", re.IGNORECASE),
        "3,000 attack/injection count is not supported by the current canonical artifact.",
    ),
    ClaimPattern(
        "stale_lineage_count",
        re.compile(r"(?:4,200|4200)[^\n]*(?:lineage|record|row|source|dataset)", re.IGNORECASE),
        "4,200 lineage/data count is not supported by the current canonical artifact.",
    ),
    ClaimPattern(
        "stale_failure_range",
        re.compile(r"139\s*[–-]\s*206|139\s*/\s*206|207[^\n]*(?:failure|under-block)", re.IGNORECASE),
        "Failure counts must use current value 139; historical counts must be labelled.",
    ),
    ClaimPattern(
        "unsupported_docker",
        re.compile(r"(docker-compose\.yml[^\n]*verified|Docker environment routes|docker compose up --build)", re.IGNORECASE),
        "Docker support is currently unverified and must not be claimed as working.",
    ),
    ClaimPattern(
        "unsupported_production_ready",
        re.compile(r"(production-ready|fully production ready|enterprise-grade)", re.IGNORECASE),
        "Production/enterprise readiness must not be claimed for the current prototype.",
    ),
    ClaimPattern(
        "unsupported_realtime",
        re.compile(r"real-time[^\n]*(?:telemetry|gateway|throughput|logs|analytics)", re.IGNORECASE),
        "Real-time operational claims require measured runtime evidence.",
    ),
    ClaimPattern(
        "unsupported_embedding_healthy",
        re.compile(r"(semantic embedding|embedding detector)[^\n]*(?:enabled|healthy|detects instruction overrides regardless)", re.IGNORECASE),
        "Embedding is optional and currently unavailable in runtime evidence.",
    ),
    ClaimPattern(
        "demo_score_claimed_as_measured",
        re.compile(r"(5\.5\s*(?:→|->)\s*8\.5\s*(?:→|->)\s*5\.5|8\.5[^\n]*5\.5)[^\n]*(?:measured|real LLM|production|validated grader)", re.IGNORECASE),
        "The deterministic 5.5→8.5→5.5 path is demo-only, not measured score-integrity evidence.",
    ),
    ClaimPattern(
        "unsupported_phase2_latency_claim",
        re.compile(r"(?:p50|p95|p99|throughput)[^\n]*(?:production|prod|capacity|SLA)", re.IGNORECASE),
        "Phase 2 operational latency is local/environment-specific and must not be presented as production capacity.",
    ),
]


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}


def canonical_metrics(root: Path) -> dict:
    combined = load_json(root / "datasets/reports/v3/benchmark_v3_combined.json")
    benchmark = combined.get("benchmark_report", {})
    evidence = combined.get("evidence_report", {})
    detector = evidence.get("detector", {})
    return {
        "source": "datasets/reports/v3/benchmark_v3_combined.json",
        "run_id": evidence.get("run_context", {}).get("run_id"),
        "git_commit": evidence.get("run_context", {}).get("git_commit"),
        "benchmark_version": benchmark.get("benchmark_id"),
        "evaluated_sample_count": benchmark.get("total_cases"),
        "dataset_total_cases": evidence.get("dataset", {}).get("total_cases"),
        "dataset_hash": evidence.get("dataset", {}).get("dataset_sha256"),
        "config_hash": detector.get("config_sha256"),
        "accuracy": benchmark.get("accuracy"),
        "precision": benchmark.get("precision"),
        "recall": benchmark.get("recall"),
        "macro_f1": benchmark.get("macro_f1"),
        "false_positive_rate": benchmark.get("false_positive_rate"),
        "under_block_rate": benchmark.get("under_block_rate"),
        "failure_count": benchmark.get("failure_analysis_count") or combined.get("failure_analysis_count"),
        "embedding_runtime_state": detector.get("embedding_runtime_state"),
        "embedding_enabled": detector.get("enable_embedding_detector"),
    }


def phase2_evidence_state(root: Path) -> dict:
    approved = load_json(root / "datasets/manifests/approved_evidence_run.json")
    track = load_json(root / "datasets/manifests/track_manifest.json")
    if not approved:
        return {
            "approved_run_id": None,
            "approved_status": "missing",
            "measured_score_integrity_status": "missing",
            "operational_environment_label": "missing",
        }

    tracks = track.get("tracks", {})
    score_integrity = tracks.get("score_integrity", {})
    measured = score_integrity.get("measured_score_integrity", {})
    operational = tracks.get("operational_reliability", {})
    return {
        "approved_run_id": approved.get("approved_run_id"),
        "approved_status": approved.get("status"),
        "approval_scope": approved.get("approval_scope"),
        "metric_definitions_version": approved.get("metric_definitions_version"),
        "measured_score_integrity_status": measured.get("status"),
        "deterministic_demo_status": score_integrity.get("deterministic_demonstration", {}).get("status"),
        "operational_environment_label": operational.get("environment_label"),
    }


def existing_frontend_routes(root: Path) -> set[str]:
    app_dir = root / "frontend/src/app"
    routes: set[str] = set()
    for page in app_dir.glob("**/page.tsx"):
        rel = page.relative_to(app_dir).parent
        route = "/" if str(rel) == "." else "/" + str(rel).replace("\\", "/")
        routes.add(route)
    return routes


def classify_line(line: str, path: str, line_no: int) -> list[dict]:
    findings = []
    for pattern in CLAIM_PATTERNS:
        if not pattern.pattern.search(line):
            continue
        if ALLOWED_CONTEXT.search(line):
            continue
        findings.append(
            {
                "file": path,
                "line": line_no,
                "claim_type": pattern.claim_type,
                "claim_text": line.strip(),
                "message": pattern.message,
            }
        )
    return findings


def scan_claims(root: Path, paths: Iterable[str]) -> list[dict]:
    findings: list[dict] = []
    for rel in paths:
        path = root / rel
        if not path.exists():
            findings.append(
                {
                    "file": rel,
                    "line": 0,
                    "claim_type": "missing_scan_target",
                    "claim_text": rel,
                    "message": "Configured public claim file is missing.",
                }
            )
            continue
        for idx, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            findings.extend(classify_line(line, rel, idx))
    return findings


def route_findings(root: Path) -> list[dict]:
    routes = existing_frontend_routes(root)
    missing = sorted(REQUIRED_FRONTEND_ROUTES - routes)
    return [
        {
            "file": "frontend/src/app",
            "line": 0,
            "claim_type": "missing_frontend_route",
            "claim_text": route,
            "message": "Required public route is missing.",
        }
        for route in missing
    ]


def docker_findings(root: Path, findings: list[dict]) -> list[dict]:
    docker_files = list(root.glob("Dockerfile*")) + list(root.glob("docker-compose*")) + list(root.glob("compose*.yml")) + list(root.glob("compose*.yaml"))
    docker_claims = [f for f in findings if f["claim_type"] == "unsupported_docker"]
    if docker_files or docker_claims:
        return []
    return []


def phase2_evidence_findings(root: Path) -> list[dict]:
    state = phase2_evidence_state(root)
    findings: list[dict] = []
    if state["approved_status"] not in {"approved", "missing"}:
        findings.append(
            {
                "file": "datasets/manifests/approved_evidence_run.json",
                "line": 0,
                "claim_type": "unapproved_phase2_evidence_run",
                "claim_text": str(state["approved_run_id"]),
                "message": "Phase 2 public measured claims may only reference approved runs.",
            }
        )
    if state["measured_score_integrity_status"] not in {"NOT_MEASURED", "missing"}:
        findings.append(
            {
                "file": "datasets/manifests/track_manifest.json",
                "line": 0,
                "claim_type": "unexpected_measured_score_integrity_status",
                "claim_text": str(state["measured_score_integrity_status"]),
                "message": "Measured score-integrity status must stay NOT_MEASURED until an approved evaluator exists.",
            }
        )
    return findings


def build_report(root: Path, scan_paths: Iterable[str]) -> dict:
    findings = scan_claims(root, scan_paths)
    findings.extend(route_findings(root))
    findings.extend(docker_findings(root, findings))
    findings.extend(phase2_evidence_findings(root))
    metrics = canonical_metrics(root)
    phase2_state = phase2_evidence_state(root)
    return {
        "status": "PASS" if not findings else "FAIL",
        "canonical_metrics": metrics,
        "phase2_evidence_state": phase2_state,
        "scan_paths": list(scan_paths),
        "findings": findings,
        "summary": {
            "finding_count": len(findings),
            "route_count": len(existing_frontend_routes(root)),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    parser.add_argument("--scan-path", action="append", help="Override scan paths; may be repeated")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    scan_paths = args.scan_path or DEFAULT_SCAN_PATHS
    report = build_report(root, scan_paths)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Public claim audit: {report['status']}")
        print(f"Canonical metric source: {report['canonical_metrics']['source']}")
        print(f"Phase 2 approved run: {report['phase2_evidence_state']['approved_run_id']}")
        print(f"Findings: {report['summary']['finding_count']}")
        for finding in report["findings"]:
            print(f"- {finding['file']}:{finding['line']} [{finding['claim_type']}] {finding['claim_text']}")

    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
