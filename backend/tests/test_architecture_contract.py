from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "docs/architecture/gradingguard_architecture_contract.json"


def load_contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def read_doc(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def assert_unique(values: list[str], name: str) -> None:
    assert len(values) == len(set(values)), f"{name} contains duplicates"


def test_architecture_contract_core_enums_are_stable() -> None:
    contract = load_contract()

    assert contract["contract_version"] == "1.0.0-phase1"
    assert contract["decision_schema_version"] == "grading_decision.v1"
    assert contract["supported_modes"] == ["shadow", "warn", "enforce", "degraded"]
    assert contract["supported_actions"] == [
        "allow",
        "warn",
        "sanitize",
        "secure_grade",
        "manual_review",
        "block",
    ]
    assert contract["detector_health_states"] == [
        "healthy",
        "warming",
        "degraded",
        "unavailable",
        "disabled",
    ]
    assert_unique(contract["error_codes"], "error_codes")
    assert_unique(contract["supported_actions"], "supported_actions")
    assert_unique(contract["supported_modes"], "supported_modes")


def test_schema_files_match_machine_contract() -> None:
    contract = load_contract()
    decision_schema = json.loads((ROOT / "schemas/grading_decision.schema.json").read_text(encoding="utf-8"))
    error_schema = json.loads((ROOT / "schemas/grading_error.schema.json").read_text(encoding="utf-8"))

    selected_action_enum = decision_schema["properties"]["selected_action"]["enum"]
    error_code_enum = error_schema["properties"]["error_code"]["enum"]

    assert selected_action_enum == contract["supported_actions"]
    assert error_code_enum == contract["error_codes"]
    for schema_path in contract["schema_files"]:
        schema = json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
        assert schema["$schema"].endswith("2020-12/schema")
        assert schema["additionalProperties"] is False
        assert schema["required"]


def test_contract_documents_exist_and_reference_required_terms() -> None:
    contract = load_contract()
    missing = [path for path in contract["contract_documents"] if not (ROOT / path).exists()]
    assert missing == []

    action_doc = read_doc("docs/architecture/action-semantics.md").lower()
    mode_doc = read_doc("docs/architecture/operating-modes.md").lower()
    error_doc = read_doc("docs/contracts/grading-gateway-api.md")

    for action in contract["supported_actions"]:
        assert action in action_doc
    for mode in contract["supported_modes"]:
        assert mode in mode_doc
    for error_code in contract["error_codes"]:
        assert error_code in error_doc


def test_review_states_are_reachable_from_pending() -> None:
    contract = load_contract()
    states = set(contract["review_statuses"])
    transitions = contract["review_transitions"]

    reached = {"pending"}
    changed = True
    while changed:
        changed = False
        for source, target in transitions:
            if source in reached and target not in reached:
                reached.add(target)
                changed = True

    assert reached == states


def test_policy_lifecycle_and_readiness_are_documented() -> None:
    contract = load_contract()
    policy_doc = read_doc("docs/contracts/policy-contract.md").lower()
    readiness_doc = read_doc("docs/product/readiness-gates.md")

    for status in contract["policy_statuses"]:
        assert status in policy_doc
    for level in contract["readiness_levels"]:
        assert level in readiness_doc
    for status in contract["readiness_status_values"]:
        assert status in readiness_doc


def test_threat_control_matrix_covers_every_threat() -> None:
    contract = load_contract()
    matrix_doc = read_doc("docs/security/threat-control-test-matrix.md")
    threat_doc = read_doc("docs/security/threat-model.md")

    for threat in contract["threats"]:
        assert threat in matrix_doc
        assert threat in threat_doc


def test_benchmark_tracks_and_frontend_ia_are_complete() -> None:
    contract = load_contract()
    benchmark_doc = read_doc("docs/benchmark/benchmark-track-contracts.md")
    frontend_doc = read_doc("docs/product/security-console-information-architecture.md")

    for track in contract["benchmark_tracks"]:
        assert track in benchmark_doc
    for route in contract["frontend_routes"]:
        assert route in frontend_doc


def test_adrs_exist_with_required_sections() -> None:
    contract = load_contract()

    for path in contract["adrs"]:
        text = read_doc(path)
        assert "Status:" in text
        assert "## Context" in text
        assert "## Decision" in text
        assert "## Alternatives considered" in text
        assert "## Consequences" in text
        assert "## Later-phase implementation impact" in text
