from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend/src"


def read(rel: str) -> str:
    return (FRONTEND / rel).read_text(encoding="utf-8")


def test_phase5_routes_exist_and_use_console_shell() -> None:
    routes = [
        "app/dashboard/page.tsx",
        "app/threat-inbox/page.tsx",
        "app/incidents/[id]/page.tsx",
        "app/manual-review/page.tsx",
        "app/policies/page.tsx",
        "app/detector-health/page.tsx",
        "app/integration-runtime/page.tsx",
        "app/benchmark/page.tsx",
        "app/evidence/page.tsx",
        "app/data-lineage/page.tsx",
        "app/attack-arena/page.tsx",
        "app/playground/page.tsx",
        "app/judge-view/page.tsx",
    ]
    for route in routes:
        source = read(route)
        assert "SecurityConsolePage" in source


def test_phase5_frontend_does_not_expose_tokens_or_unsafe_html() -> None:
    combined = "\n".join(path.read_text(encoding="utf-8") for path in FRONTEND.rglob("*.tsx"))
    api = read("lib/security-api.ts")
    assert "dangerouslySetInnerHTML" not in combined
    assert "localStorage" not in combined
    assert "sessionStorage" not in combined
    assert "console.log" not in combined
    assert "access_token" not in combined
    assert "localStorage" not in api
    assert "sessionStorage" not in api
    assert "console.log" not in api


def test_phase5_truth_labels_are_visible() -> None:
    source = read("components/SecurityConsole.tsx")
    required = [
        "LOW_SUPPORT",
        "NOT_MEASURED",
        "DETERMINISTIC_DEMO",
        "PRODUCTION NOT READY",
        "Pilot local",
        "phase3_final_detection_engine",
        "phase4_operational_safety",
    ]
    for label in required:
        assert label in source


def test_phase5_uses_single_icon_system_and_gau_tokens() -> None:
    shell = read("components/AppShell.tsx")
    console = read("components/SecurityConsole.tsx")
    css = read("app/globals.css")
    assert 'from "lucide-react"' in shell
    assert 'from "lucide-react"' in console
    assert "react-icons" not in shell + console
    assert "@heroicons" not in shell + console
    for token in ["--gg-primary", "--gg-surface", "--gg-critical", "--gg-degraded", "--gg-radius"]:
        assert token in css


def test_phase5_mutations_use_idempotency_and_expected_versions() -> None:
    api = read("lib/security-api.ts")
    for phrase in [
        "idempotencyKey",
        "expected_version: review.version",
        "expected_version: runtime.mode.version",
        "restricted-evidence",
        "stateForError",
    ]:
        assert phrase in api
