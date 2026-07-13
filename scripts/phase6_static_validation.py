#!/usr/bin/env python3
"""Static Phase 6A deployment/reproducibility validation.

This gate intentionally avoids Docker and browser execution. It checks that
the repo preserves truthful readiness boundaries and that environment/build
contracts are in place before Phase 6B runtime verification happens elsewhere.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

EXPECTED_FRONTEND_VERSIONS = {
    "dependencies": {
        "next": "16.2.10",
        "react": "19.2.4",
        "react-dom": "19.2.4",
    },
    "devDependencies": {
        "@playwright/test": "1.61.1",
        "@axe-core/playwright": "4.12.1",
    },
}

REQUIRED_BACKEND_ENV = {
    "APP_NAME",
    "ENV",
    "MOCK_LLM",
    "FRONTEND_ORIGIN",
    "CORS_ALLOWED_ORIGINS",
    "SECURITY_DATABASE_URL",
    "TEST_DATABASE_URL",
    "AUTH_TOKEN_SECRET",
    "AUTH_ISSUER",
    "AUTH_AUDIENCE",
    "MAX_CANDIDATE_CONTENT_CHARS",
    "MAX_REQUEST_BODY_CHARS",
    "RATE_LIMIT_WINDOW_SECONDS",
    "RATE_LIMIT_MAX_REQUESTS",
}

REQUIRED_FRONTEND_ENV = {
    "NEXT_PUBLIC_API_URL",
    "PHASE5_E2E_FRONTEND_PORT",
    "PHASE5_E2E_BACKEND_PORT",
    "PHASE5_E2E_EXTERNAL_SERVERS",
    "PHASE5_E2E_NODE_BIN_DIR",
}

REQUIRED_DOCKERIGNORE_PATTERNS = {
    ".git",
    "**/__pycache__/",
    "frontend/node_modules",
    "frontend/.next",
    "frontend/.playwright-artifacts",
    "frontend/.playwright-e2e",
    "frontend/playwright-report",
    "frontend/test-results",
    "datasets/reports/v3/",
    "datasets/evidence/",
    "*.pem",
    "*.log",
}

SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----"),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
]

TEXT_EXTENSIONS = {
    ".env",
    ".example",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yml",
    ".yaml",
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def env_keys(path: str) -> set[str]:
    keys: set[str] = set()
    for line in read(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        keys.add(stripped.split("=", 1)[0])
    return keys


def tracked_files() -> list[Path]:
    import subprocess

    output = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    return [ROOT / line for line in output.splitlines() if line]


def check_versions(findings: list[dict]) -> None:
    package = json.loads(read("frontend/package.json"))
    for section, expected in EXPECTED_FRONTEND_VERSIONS.items():
        actual_section = package.get(section, {})
        for name, expected_version in expected.items():
            actual = actual_section.get(name)
            if actual != expected_version:
                findings.append(
                    {
                        "check": "pinned_frontend_versions",
                        "file": "frontend/package.json",
                        "message": f"{name} expected {expected_version}, got {actual}",
                    }
                )


def check_env_examples(findings: list[dict]) -> None:
    backend_keys = env_keys("backend/.env.example")
    frontend_keys = env_keys("frontend/.env.example")
    for key in sorted(REQUIRED_BACKEND_ENV - backend_keys):
        findings.append({"check": "backend_env_example", "file": "backend/.env.example", "message": f"missing {key}"})
    for key in sorted(REQUIRED_FRONTEND_ENV - frontend_keys):
        findings.append({"check": "frontend_env_example", "file": "frontend/.env.example", "message": f"missing {key}"})


def check_docker_boundaries(findings: list[dict]) -> None:
    dockerignore = set(line.strip() for line in read(".dockerignore").splitlines() if line.strip() and not line.startswith("#"))
    for pattern in sorted(REQUIRED_DOCKERIGNORE_PATTERNS - dockerignore):
        findings.append({"check": "dockerignore_boundary", "file": ".dockerignore", "message": f"missing {pattern}"})

    dockerfile = read("frontend/e2e/Dockerfile.playwright-webkit")
    required_fragments = [
        "not a production deployment image",
        "mcr.microsoft.com/playwright:v1.61.1-noble",
        "PHASE5_E2E_EXTERNAL_SERVERS=1",
        "--project=webkit-desktop",
        "--project=mobile-ios",
    ]
    for fragment in required_fragments:
        if fragment not in dockerfile:
            findings.append({"check": "webkit_test_dockerfile", "file": "frontend/e2e/Dockerfile.playwright-webkit", "message": f"missing {fragment}"})


def check_playwright_external_mode(findings: list[dict]) -> None:
    config = read("frontend/playwright.config.ts")
    if "PHASE5_E2E_EXTERNAL_SERVERS" not in config or "webServer: USE_EXTERNAL_SERVERS ? undefined" not in config:
        findings.append(
            {
                "check": "playwright_external_server_mode",
                "file": "frontend/playwright.config.ts",
                "message": "external-server mode must disable nested Playwright webServer startup",
            }
        )


def check_truthful_phase_state(findings: list[dict]) -> None:
    adr = read("docs/adr/ADR-011-phase5-waiver-and-phase6-authorization.md")
    report = read("docs/phase6_deployment_reproducibility_report.md")
    contract = read("docs/contracts/environment-contract.md")
    combined = "\n".join([adr, report, contract])
    required = [
        "PHASE_5_FRONTEND_SECURITY_CONSOLE_PARTIAL",
        "VERIFICATION_DEBT: OPEN",
        "PHASE_6: AUTHORIZED",
        "PRODUCTION_READY: NOT_READY",
        "Docker runtime | `UNAVAILABLE`",
        "Docker deployment verified | `false`",
        "WebKit container execution | `NOT_RUN`",
    ]
    for phrase in required:
        if phrase not in combined:
            findings.append({"check": "truthful_phase_state", "file": "docs/phase6*", "message": f"missing {phrase}"})


def check_static_workflow(findings: list[dict]) -> None:
    workflow = ROOT / ".github/workflows/phase6-static.yml"
    if not workflow.exists():
        findings.append({"check": "phase6_static_workflow", "file": ".github/workflows/phase6-static.yml", "message": "workflow missing"})
        return
    source = workflow.read_text(encoding="utf-8")
    required = [
        "python3 scripts/phase6_static_validation.py",
        "python3 scripts/audit_public_claims.py",
        "python3 scripts/phase6_environment_audit.py",
    ]
    for phrase in required:
        if phrase not in source:
            findings.append({"check": "phase6_static_workflow", "file": ".github/workflows/phase6-static.yml", "message": f"missing {phrase}"})
    if re.search(r"\bdocker\b", source, re.IGNORECASE):
        findings.append({"check": "phase6_static_workflow", "file": ".github/workflows/phase6-static.yml", "message": "static workflow must not invoke Docker"})


def check_secrets(findings: list[dict]) -> None:
    for path in tracked_files():
        rel = path.relative_to(ROOT)
        if any(part in {".git", "node_modules", ".next", ".playwright-artifacts", ".playwright-e2e", "__pycache__"} for part in rel.parts):
            continue
        if path.suffix not in TEXT_EXTENSIONS and path.name not in {".dockerignore", "Dockerfile.playwright-webkit"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append({"check": "secret_scan", "file": str(rel), "message": f"matched {pattern.pattern}"})


def build_report() -> dict:
    findings: list[dict] = []
    check_versions(findings)
    check_env_examples(findings)
    check_docker_boundaries(findings)
    check_playwright_external_mode(findings)
    check_truthful_phase_state(findings)
    check_static_workflow(findings)
    check_secrets(findings)
    return {
        "status": "PASS" if not findings else "FAIL",
        "phase": "phase6a_non_docker_environment_hardening",
        "docker_runtime_required": False,
        "docker_verified": False,
        "webkit_verified": False,
        "production_ready": False,
        "findings": findings,
        "summary": {"finding_count": len(findings)},
    }


def main() -> int:
    report = build_report()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
