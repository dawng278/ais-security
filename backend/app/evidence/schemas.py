from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DatasetFingerprint(BaseModel):
    dataset_path: str
    dataset_version: str
    dataset_sha256: str
    total_cases: int
    label_distribution: Dict[str, int] = Field(default_factory=dict)
    split_distribution: Dict[str, int] = Field(default_factory=dict)
    attack_type_distribution: Dict[str, int] = Field(default_factory=dict)
    language_distribution: Dict[str, int] = Field(default_factory=dict)


class DetectorConfigSnapshot(BaseModel):
    detector_version: str = "ensemble_v3"
    threshold_version: str = "risk_policy_v3"
    enable_embedding_detector: bool = True
    enable_classifier_detector: bool = False
    risk_thresholds: Dict[str, float] = Field(default_factory=dict)
    config_sha256: Optional[str] = None


class BenchmarkRunContext(BaseModel):
    run_id: str
    created_at: str
    git_commit: Optional[str] = None
    random_seed: int = 42
    environment: str = "local"


class EvidenceMetricSummary(BaseModel):
    overall_metrics: Dict[str, float] = Field(default_factory=dict)
    score_integrity_metrics: Dict[str, float] = Field(default_factory=dict)
    sanitizer_metrics: Dict[str, float] = Field(default_factory=dict)
    latency_metrics: Dict[str, float] = Field(default_factory=dict)


class EvidenceReport(BaseModel):
    run_context: BenchmarkRunContext
    dataset: DatasetFingerprint
    detector: DetectorConfigSnapshot
    metrics: EvidenceMetricSummary
    failure_case_count: int = 0
    report_paths: Dict[str, str] = Field(default_factory=dict)
    notes: List[str] = Field(default_factory=list)
