import json
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DataSourceLineage(BaseModel):
    source_id: str
    platform: str
    purpose: str
    license_status: str
    raw_rows: int
    accepted_rows: int
    rejected_rows: int
    notes: str


class TransformStage(BaseModel):
    stage: str
    input_rows: int
    output_rows: int
    rejected_rows: int
    reason: str


class DatasetLineageReport(BaseModel):
    dataset_version: str
    dataset_sha256: Optional[str] = None
    sources: List[DataSourceLineage] = Field(default_factory=list)
    stages: List[TransformStage] = Field(default_factory=list)
    split_distribution: Dict[str, int] = Field(default_factory=dict)
    label_distribution: Dict[str, int] = Field(default_factory=dict)
    attack_type_distribution: Dict[str, int] = Field(default_factory=dict)
    language_distribution: Dict[str, int] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)


def resolve_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "datasets").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent.parent


def get_seeded_lineage_report() -> DatasetLineageReport:
    return DatasetLineageReport(
        dataset_version="gradingguard_benchmark_v3_demo",
        dataset_sha256="demo_sha256_pending_real_benchmark_run",
        sources=[
            DataSourceLineage(
                source_id="hf_zachz_prompt_injection_benchmark",
                platform="Hugging Face",
                purpose="external prompt injection benchmark",
                license_status="MIT",
                raw_rows=303,
                accepted_rows=292,
                rejected_rows=11,
                notes="Used for external validation of injection vs benign prompts.",
            ),
            DataSourceLineage(
                source_id="hf_neuralchemy_prompt_injection",
                platform="Hugging Face",
                purpose="train/validation prompt injection",
                license_status="check_required",
                raw_rows=1200,
                accepted_rows=1104,
                rejected_rows=96,
                notes="Used for generic prompt injection and jailbreak category diversity.",
            ),
            DataSourceLineage(
                source_id="hf_deepset_prompt_injections",
                platform="Hugging Face",
                purpose="external prompt injection benchmark",
                license_status="check_required",
                raw_rows=600,
                accepted_rows=560,
                rejected_rows=40,
                notes="Used as baseline binary detection data.",
            ),
            DataSourceLineage(
                source_id="hf_mindgard_evaded_samples",
                platform="Hugging Face",
                purpose="evasion benchmark",
                license_status="check_required",
                raw_rows=500,
                accepted_rows=455,
                rejected_rows=45,
                notes="Used for obfuscated and adversarially mutated prompt injection samples.",
            ),
            DataSourceLineage(
                source_id="kaggle_prompt_injection_benign",
                platform="Kaggle",
                purpose="train/validation prompt injection",
                license_status="check_required",
                raw_rows=800,
                accepted_rows=742,
                rejected_rows=58,
                notes="Used for benign prompt and malicious prompt diversity.",
            ),
            DataSourceLineage(
                source_id="ielts_clean_pool",
                platform="Self-built + open IELTS samples",
                purpose="clean IELTS base essays",
                license_status="demo_safe_subset",
                raw_rows=300,
                accepted_rows=280,
                rejected_rows=20,
                notes="Used to create IELTS-domain injected attack variants.",
            ),
            DataSourceLineage(
                source_id="self_built_hard_negatives",
                platform="Self-built",
                purpose="hard negative false positive evaluation",
                license_status="owned",
                raw_rows=120,
                accepted_rows=120,
                rejected_rows=0,
                notes="Benign cybersecurity discussion samples that should not be blocked.",
            ),
        ],
        stages=[
            TransformStage(
                stage="raw_import",
                input_rows=3823,
                output_rows=3823,
                rejected_rows=0,
                reason="Imported rows from registered sources.",
            ),
            TransformStage(
                stage="license_registry",
                input_rows=3823,
                output_rows=3823,
                rejected_rows=0,
                reason="License status and source purpose tracked per dataset.",
            ),
            TransformStage(
                stage="schema_adapter",
                input_rows=3823,
                output_rows=3650,
                rejected_rows=173,
                reason="Rows missing required text, label, or source metadata were rejected.",
            ),
            TransformStage(
                stage="deduplication",
                input_rows=3650,
                output_rows=3380,
                rejected_rows=270,
                reason="Duplicate and near-duplicate prompts were removed.",
            ),
            TransformStage(
                stage="quality_filter",
                input_rows=3380,
                output_rows=3275,
                rejected_rows=105,
                reason="Too short, empty, malformed, or invalid rows were removed.",
            ),
            TransformStage(
                stage="attack_transformation",
                input_rows=3275,
                output_rows=4200,
                rejected_rows=0,
                reason="Clean IELTS essays were transformed into domain-specific injected variants.",
            ),
            TransformStage(
                stage="group_aware_split",
                input_rows=4200,
                output_rows=4200,
                rejected_rows=0,
                reason="Samples were split by group_id to prevent clean/injected variants leaking across splits.",
            ),
            TransformStage(
                stage="dataset_hashing",
                input_rows=4200,
                output_rows=4200,
                rejected_rows=0,
                reason="Final benchmark dataset fingerprint was generated.",
            ),
        ],
        split_distribution={
            "train": 2100,
            "validation": 700,
            "public_test": 700,
            "private_holdout": 700,
        },
        label_distribution={
            "clean": 700,
            "benign": 500,
            "injection": 3000,
        },
        attack_type_distribution={
            "direct_english": 420,
            "direct_vietnamese": 420,
            "direct_chinese": 320,
            "role_spoofing": 360,
            "unicode_obfuscation": 360,
            "base64_instruction": 320,
            "indirect_injection": 420,
            "delimiter_injection": 280,
            "benign_security_discussion": 500,
            "clean": 700,
        },
        language_distribution={
            "en": 2800,
            "vi": 700,
            "zh": 320,
            "mixed": 380,
        },
        notes=[
            "This is a seeded demo lineage report. Run Benchmark v3 to generate real lineage metadata.",
            "External dataset licenses marked check_required must be verified before redistribution.",
            "Group-aware splitting prevents variants of the same base essay from appearing in both train and test splits.",
        ],
    )


def get_lineage_report() -> DatasetLineageReport:
    root = resolve_project_root()
    evidence_path = root / "datasets" / "reports" / "v3" / "evidence" / "evidence_report.json"

    if not evidence_path.exists():
        return get_seeded_lineage_report()

    try:
        data = json.loads(evidence_path.read_text(encoding="utf-8"))
        dataset = data.get("dataset", {})

        seeded = get_seeded_lineage_report()

        model_update = {
            "dataset_version": dataset.get("dataset_version", seeded.dataset_version),
            "dataset_sha256": dataset.get("dataset_sha256", seeded.dataset_sha256),
            "split_distribution": dataset.get("split_distribution", seeded.split_distribution),
            "label_distribution": dataset.get("label_distribution", seeded.label_distribution),
            "attack_type_distribution": dataset.get("attack_type_distribution", seeded.attack_type_distribution),
            "language_distribution": dataset.get("language_distribution", seeded.language_distribution),
            "notes": [
                "Lineage report is using the latest Benchmark v3 evidence fingerprint.",
                "Source-level row counts may use registry/demo values unless a full lineage build has been run.",
            ],
        }

        if hasattr(seeded, "model_copy"):
            return seeded.model_copy(update=model_update)
        else:
            return seeded.copy(update=model_update)

    except Exception:
        return get_seeded_lineage_report()
