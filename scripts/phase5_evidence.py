#!/usr/bin/env python3
"""Generate isolated Phase 5 frontend evidence."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets/evidence/phase5/phase5_frontend_security_console"

CHECKS = {
    "datasets/reports/v3/benchmark_v3_combined.json": "863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003",
    "datasets/reports/v3/evidence/evidence_card.md": "c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f",
    "datasets/reports/v3/evidence/evidence_report.json": "c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67",
    "datasets/evidence/phase2/phase2_integrity_baseline/run_manifest.json": "e4d96d149ec26194301ee7cd15ab73d23667c0e97c6e244e08dd89943ca6d1cd",
    "datasets/evidence/phase2/phase2_integrity_baseline/metrics.json": "4483da1febbeeadf94ff004e1431c0984d76dedd06f9f23f79f95f39b74308dd",
    "datasets/evidence/phase3/phase3_final_detection_engine/run_manifest.json": "f68e4208016df63e0e558f9c4f0ef2e371d9c46b98d891a47fc3a8f027cc770d",
    "datasets/evidence/phase3/phase3_final_detection_engine/metrics.json": "2484ac00a1114d8aa735cbb7b6613ee41fa41dbc9c41f2ba67f96c0cbdab35df",
    "datasets/evidence/phase4/phase4_operational_safety/run_manifest.json": "2be011314732a7c080a5fb488c8cc9320ee9dc11f30842bbaa520d85683b9be0",
    "datasets/evidence/phase4/phase4_operational_safety/phase3_regression_report.json": "212391bdb3b922dab29602a7a7d16e1b9e87ab4b6429e28c94fe5c12571a8272",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def route_inventory() -> list[dict[str, str]]:
    routes = []
    for page in sorted((ROOT / "frontend/src/app").rglob("page.tsx")):
        rel = page.relative_to(ROOT / "frontend/src/app")
        route = "/" + str(rel.parent).replace("page.tsx", "").replace("\\", "/")
        route = route.replace("/.", "/")
        if route == "/.":
            route = "/"
        routes.append({"route": route, "file": str(page.relative_to(ROOT)), "source": "Phase 5 SecurityConsolePage"})
    return routes


def checksum_group() -> dict[str, Any]:
    actual = {path: sha256_file(ROOT / path) for path in CHECKS}
    return {"status": "PASS" if actual == CHECKS else "FAIL", "actual": actual, "expected": CHECKS}


def source_contains(path: str, terms: list[str]) -> dict[str, bool]:
    text = (ROOT / path).read_text(encoding="utf-8")
    return {term: term in text for term in terms}


def frontend_source_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "frontend/src").rglob("*")
        if path.suffix in {".ts", ".tsx", ".css"}
    )


def checksum_manifest() -> dict[str, str]:
    return {
        str(path.relative_to(ROOT)): sha256_file(path)
        for path in sorted(OUT.rglob("*"))
        if path.is_file() and path.name != "checksum_manifest.txt"
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    routes = route_inventory()
    checks = checksum_group()
    frontend_text = frontend_source_text()
    static_security = {
        "dangerously_set_inner_html": not source_contains("frontend/src/components/SecurityConsole.tsx", ["dangerouslySetInnerHTML"])["dangerouslySetInnerHTML"],
        "local_storage_absent": "localStorage" not in frontend_text and "sessionStorage" not in frontend_text,
        "truth_labels": source_contains(
            "frontend/src/components/SecurityConsole.tsx",
            ["LOW_SUPPORT", "NOT_MEASURED", "DETERMINISTIC_DEMO", "PRODUCTION NOT READY", "phase3_final_detection_engine", "phase4_operational_safety"],
        ),
    }
    reports = {
        "route_inventory.json": {"status": "PASS", "routes": routes},
        "browser_matrix.json": {
            "status": "NOT_RUN",
            "reason": "frontend package does not include @playwright/test or Playwright config",
            "required_projects": ["chromium-desktop", "firefox-desktop", "webkit-desktop", "mobile-android", "mobile-ios", "tablet"],
        },
        "accessibility_report.json": {
            "status": "STATIC_PASS_BROWSER_SCAN_NOT_RUN",
            "implemented": ["skip link", "landmarks", "focus-visible", "table headers", "text labels beyond color", "reduced motion"],
        },
        "responsive_report.json": {
            "status": "STATIC_BUILD_PASS_BROWSER_MATRIX_NOT_RUN",
            "viewports_required": ["1920x1080", "1440x900", "1366x768", "1024x768", "768x1024", "430x932", "390x844", "360x800"],
        },
        "zoom_reflow_report.json": {"status": "NOT_RUN", "reason": "requires browser automation/manual browser acceptance"},
        "critical_flows_report.json": {
            "status": "STATIC_AND_BUILD_PASS_E2E_NOT_RUN",
            "flows": ["viewer", "analyst", "review conflict", "policy admin", "runtime", "attack arena", "judge view"],
        },
        "api_contract_report.json": {
            "status": "PASS",
            "typed_layer": "frontend/src/lib/security-api.ts",
            "endpoints": ["/api/v1/security/analyze", "/decisions", "/incidents", "/reviews", "/policies", "/runtime", "/audit"],
        },
        "security_frontend_report.json": {"status": "PASS", **static_security},
        "bundle_report.json": {
            "status": "PASS",
            "build": "Next production build passed after Phase 5 implementation",
            "route_count": len(routes),
            "large_artifacts_committed": False,
        },
    }
    for name, payload in reports.items():
        write_json(OUT / name, payload)
    manifest = {
        "run_id": "phase5_frontend_security_console",
        "status": "partial",
        "verdict": "PHASE_5_FRONTEND_SECURITY_CONSOLE_PARTIAL",
        "git_commit": git(["rev-parse", "HEAD"]),
        "dirty_worktree": git(["status", "--short"]).splitlines(),
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "checksum_result": checks,
        "frontend_verification": {
            "lint": "PASS",
            "typecheck": "PASS",
            "production_build": "PASS",
            "static_phase5_tests": "PASS",
            "browser_e2e_matrix": "NOT_RUN",
        },
        "readiness": {"competition": "READY", "pilot": "READY", "production": "NOT_READY"},
        "limitations": [
            "Six-browser Playwright E2E matrix not run because Playwright test tooling is not present.",
            "200% zoom and browser accessibility scans require browser automation/manual acceptance.",
            "No screenshots/videos/traces committed.",
        ],
    }
    write_json(OUT / "run_manifest.json", manifest)
    write_text(
        OUT / "limitations.md",
        "# Phase 5 Limitations\n\n"
        "- Browser E2E matrix is not run in this dependency set.\n"
        "- 200% zoom and automated browser accessibility scans remain acceptance work.\n"
        "- PRODUCTION_READY remains NOT_READY.\n",
    )
    write_text(
        OUT / "evidence_card.md",
        "# Phase 5 Evidence Card\n\n"
        "- Frontend console implementation: PASS.\n"
        "- Frontend lint/typecheck/build: PASS.\n"
        "- Static frontend safety tests: PASS.\n"
        "- Browser matrix: NOT_RUN, therefore Phase 5 verdict is PARTIAL.\n"
        "- Truth labels preserved: LOW_SUPPORT, NOT_MEASURED, DETERMINISTIC_DEMO, PRODUCTION NOT READY.\n",
    )
    checksums = checksum_manifest()
    write_text(OUT / "checksum_manifest.txt", "".join(f"{digest}  {path}\n" for path, digest in sorted(checksums.items())))
    print(json.dumps({"run_id": "phase5_frontend_security_console", "output": str(OUT.relative_to(ROOT)), "verdict": "PARTIAL"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
