from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOLS_PATH = ROOT / "scripts/phase2_dataset_tools.py"
SPEC = importlib.util.spec_from_file_location("phase2_dataset_tools", TOOLS_PATH)
assert SPEC and SPEC.loader
tools = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tools)


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def read_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in (ROOT / path).read_text(encoding="utf-8").splitlines() if line.strip()]


def test_source_registry_required_fields_and_approved_states() -> None:
    registry = read_json("datasets/manifests/source_registry.json")
    source_ids = [source["source_id"] for source in registry["sources"]]
    assert len(source_ids) == len(set(source_ids))
    required = {
        "source_id",
        "source_name",
        "canonical_url",
        "revision",
        "retrieval_date",
        "license_identifier",
        "license_url",
        "license_verified_at",
        "allowed_use",
        "redistribution_allowed",
        "modifications",
        "records_used",
        "source_hash",
        "independence_group",
        "approval_state",
        "reviewer_notes",
    }
    allowed = {"APPROVED", "APPROVED_WITH_RESTRICTIONS", "INTERNAL_SYNTHETIC"}
    for source in registry["sources"]:
        assert required <= set(source)
        assert source["approval_state"] in allowed
        assert source["source_hash"]


def test_canonical_sample_schema_values_and_hashes() -> None:
    samples = read_jsonl("datasets/canonical/phase2_canonical_security_samples.jsonl")
    assert samples
    allowed_tracks = {"generic_prompt_injection", "ielts_domain_security", "score_integrity", "operational_reliability"}
    for sample in samples:
        assert sample["schema_version"] == "canonical_security_sample.v1"
        assert sample["sample_id"] == tools.stable_sample_id(
            sample["source_id"],
            sample["source_record_id"],
            sample["normalized_hash"],
        )
        assert sample["content_hash"] == tools.sha256_text(sample["content"])
        assert sample["normalized_hash"] == tools.sha256_text(tools.normalize_for_hash(sample["content"]))
        assert set(sample["benchmark_tracks"]) <= allowed_tracks
        assert sample["expected_action_range"]
        assert sample["provenance"]["human_review_status"] in {
            "unreviewed",
            "single_reviewed",
            "double_reviewed",
            "adjudicated",
            "rejected",
        }


def test_split_generation_is_deterministic() -> None:
    first = tools.build_canonical_dataset(ROOT)
    second = tools.build_canonical_dataset(ROOT)
    assert tools.dataset_hash(first) == tools.dataset_hash(second)
    assert tools.split_hash(first) == tools.split_hash(second)
    manifest = read_json("datasets/manifests/split_manifest.json")
    assert manifest["algorithm_version"] == "phase2_group_hash_v1"
    assert manifest["seed"] == "gradingguard_phase2_seed_20260713"
    assert manifest["split_hash"] == tools.split_hash(first)


def test_dedup_near_duplicate_and_leakage_reports_are_gated() -> None:
    dedup = read_json("datasets/manifests/deduplication_report.json")
    near = read_json("datasets/manifests/near_duplicate_report.json")
    leakage = read_json("datasets/manifests/leakage_report.json")
    assert dedup["unresolved_measured_duplicate_count"] == 0
    assert near["algorithm_version"] == "phase2_token_jaccard_v1"
    assert near["embedding_used"] is False
    assert near["threshold"] == 0.92
    assert leakage["unresolved_holdout_leakage_count"] == 0


def test_metric_definitions_and_failure_taxonomy_are_frozen() -> None:
    metrics = read_json("datasets/manifests/metric_definitions.json")
    taxonomy = read_json("datasets/manifests/failure_taxonomy.json")
    assert metrics["version"] == "phase2_metrics_v1"
    for metric in ["accuracy", "precision", "recall", "macro_f1", "FPR", "FNR", "under_block_rate", "score_drift", "detector_availability"]:
        assert metric in metrics["metrics"]
    for category in ["false_negative", "false_positive", "under_block", "detector_unavailable", "source_conflict"]:
        assert category in taxonomy["categories"]


def test_track_manifest_separates_demo_from_measured_score_integrity() -> None:
    track = read_json("datasets/manifests/track_manifest.json")["tracks"]
    assert track["generic_prompt_injection"]["total_samples"] == 662
    assert track["ielts_domain_security"]["total_samples"] == 27
    score = track["score_integrity"]
    assert score["deterministic_demonstration"]["status"] == "DEMO_ONLY"
    assert score["measured_score_integrity"]["status"] == "NOT_MEASURED"
    assert score["measured_score_integrity"]["hard_coded_demo_results_allowed"] is False


def test_operational_reliability_is_local_and_contains_failure_labels() -> None:
    track = read_json("datasets/manifests/track_manifest.json")["tracks"]["operational_reliability"]
    assert track["status"] == "LOCAL_BENCHMARK"
    assert track["scenario_count"] == 12
    assert "not production capacity" in track["environment_label"]
    assert track["detector_availability"]["embedding"]["runtime_state"] in {
        "healthy",
        "warming",
        "degraded",
        "unavailable",
        "disabled",
    }


def test_evidence_bundle_complete_and_protected_reports_unchanged() -> None:
    approved = read_json("datasets/manifests/approved_evidence_run.json")
    assert approved["status"] == "approved"
    evidence_dir = ROOT / approved["evidence_path"]
    for name in [
        "run_manifest.json",
        "metrics.json",
        "confusion_matrix.json",
        "failure_analysis.jsonl",
        "environment.json",
        "detector_health.json",
        "dataset_manifest.json",
        "checksum_manifest.json",
        "evidence_card.md",
    ]:
        assert (evidence_dir / name).exists()

    manifest = json.loads((evidence_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["metric_definitions_version"] == "phase2_metrics_v1"
    assert manifest["protected_report_checksums"] == {
        "datasets/reports/v3/benchmark_v3_combined.json": "863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003",
        "datasets/reports/v3/evidence/evidence_card.md": "c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f",
        "datasets/reports/v3/evidence/evidence_report.json": "c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67",
    }


def test_read_only_integrity_gate_passes() -> None:
    ok, errors = tools.validate_integrity(ROOT)
    assert ok, errors
