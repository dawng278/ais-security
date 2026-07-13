#!/usr/bin/env python3
"""Generate Phase 6 deployment/reproducibility environment audit evidence."""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datasets/evidence/phase6/phase6_deployment_reproducibility"

PROTECTED_CHECKS = {
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


def run(args: list[str], cwd: Path = ROOT) -> dict[str, Any]:
    try:
        completed = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    except FileNotFoundError as exc:
        return {"status": "UNAVAILABLE", "command": args, "error": str(exc)}
    return {
        "status": "PASS" if completed.returncode == 0 else "FAIL",
        "command": args,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def package_versions() -> dict[str, Any]:
    package = json.loads((ROOT / "frontend/package.json").read_text(encoding="utf-8"))
    dev = package.get("devDependencies", {})
    node_bin = "/home/dawngbeo/Documents/study-code/.tools/node-v20.19.2-linux-x64/bin/node"
    npm_bin = "/home/dawngbeo/Documents/study-code/.tools/node-v20.19.2-linux-x64/bin/npm"
    return {
        "node": run([node_bin, "--version"]),
        "npm": run([npm_bin, "--version"]),
        "playwright": dev.get("@playwright/test"),
        "axe_playwright": dev.get("@axe-core/playwright"),
        "next": package.get("dependencies", {}).get("next"),
    }


def protected_checksums() -> dict[str, Any]:
    actual = {path: sha256_file(ROOT / path) for path in PROTECTED_CHECKS}
    return {"status": "PASS" if actual == PROTECTED_CHECKS else "FAIL", "expected": PROTECTED_CHECKS, "actual": actual}


def docker_status() -> dict[str, Any]:
    docker = shutil.which("docker")
    if not docker:
        return {
            "status": "UNAVAILABLE",
            "docker_cli": None,
            "preferred_image": "mcr.microsoft.com/playwright:v1.61.1-noble",
            "verified": False,
            "reason": "docker CLI is unavailable in this environment",
        }
    manifest = run([docker, "manifest", "inspect", "mcr.microsoft.com/playwright:v1.61.1-noble"])
    return {
        "status": "PASS" if manifest["status"] == "PASS" else "FAIL",
        "docker_cli": docker,
        "preferred_image": "mcr.microsoft.com/playwright:v1.61.1-noble",
        "manifest": manifest,
        "verified": manifest["status"] == "PASS",
    }


def phase6_static_validation() -> dict[str, Any]:
    result = run([sys.executable, "scripts/phase6_static_validation.py"])
    parsed: dict[str, Any] | None = None
    if result["status"] == "PASS" and result.get("stdout"):
        try:
            parsed = json.loads(result["stdout"])
        except json.JSONDecodeError:
            parsed = None
    return {
        "status": result["status"],
        "command": result["command"],
        "parsed": parsed,
        "stdout": result.get("stdout"),
        "stderr": result.get("stderr"),
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    docker = docker_status()
    static_validation = phase6_static_validation()
    manifest = {
        "run_id": "phase6_deployment_reproducibility",
        "status": "STARTED",
        "verdict": "PHASE_6_STARTED_ENVIRONMENT_HARDENING_PARTIAL",
        "git_commit": git(["rev-parse", "HEAD"]),
        "dirty_worktree": git(["status", "--short"]).splitlines(),
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "phase5_waiver": {
            "formal_verdict": "PHASE_5_FRONTEND_SECURITY_CONSOLE_PARTIAL",
            "implementation": "ACCEPTED",
            "verification_debt": "OPEN",
            "phase6": "AUTHORIZED",
        },
        "protected_checksums": protected_checksums(),
        "versions": package_versions(),
        "docker": docker,
        "phase6a_static_validation": static_validation,
        "artifacts": {
            "webkit_test_image_dockerfile": "frontend/e2e/Dockerfile.playwright-webkit",
            "dockerignore": ".dockerignore",
            "environment_contract": "docs/contracts/environment-contract.md",
            "deployment_reproducibility_runbook": "docs/operations/deployment-reproducibility-runbook.md",
            "manual_acceptance_checklist": "docs/frontend/phase5-manual-browser-acceptance.md",
            "static_validation_workflow": ".github/workflows/phase6-static.yml",
        },
        "readiness": {
            "demo": "READY_WITH_ENVIRONMENTAL_WAIVER",
            "competition_submission": "NOT_READY",
            "production": "NOT_READY",
            "docker_deployment_verified": False,
        },
        "limitations": [
            "Docker cannot be verified in this local environment because docker CLI is unavailable.",
            "The Playwright WebKit container artifact is test-only and unverified until built/run in a clean Docker environment.",
            "Phase 5 WebKit/iOS and human manual acceptance debt remains open.",
        ],
    }
    write_json(OUT / "run_manifest.json", manifest)
    write_json(OUT / "environment_audit.json", manifest)
    write_text(
        OUT / "limitations.md",
        "# Phase 6 Limitations\n\n"
        "- Docker CLI is unavailable locally; container build/run is NOT_RUN.\n"
        "- Docker/WebKit artifacts are test-only until verified in a clean environment.\n"
        "- PRODUCTION_READY remains NOT_READY.\n",
    )
    checksums = {
        str(path.relative_to(ROOT)): sha256_file(path)
        for path in sorted(OUT.rglob("*"))
        if path.is_file() and path.name != "checksum_manifest.txt"
    }
    write_text(OUT / "checksum_manifest.txt", "".join(f"{digest}  {path}\n" for path, digest in sorted(checksums.items())))
    print(json.dumps({"run_id": manifest["run_id"], "verdict": manifest["verdict"], "docker": docker["status"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
