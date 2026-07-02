from typing import Literal, Optional, List
from pydantic import BaseModel, Field


class BenchmarkSample(BaseModel):
    id: str
    source: str
    task_type: Literal["writing", "speaking", "generic"] = "writing"
    domain: Literal["ielts", "generic_llm_security"] = "ielts"
    language: str = "en"
    text: str
    original_text: Optional[str] = None
    label: Literal["clean", "benign", "injection"]
    attack_type: str
    attack_family: Optional[str] = None
    obfuscation_type: Optional[str] = None
    injected_span: Optional[str] = None
    expected_action: Literal["allow", "warn", "secure_grade", "manual_review"]
    expected_risk_level: Literal["low", "medium", "high", "critical"]
    clean_band: Optional[float] = None
    split: Literal["train", "validation", "public_test", "private_holdout"] = "public_test"
    group_id: str


class BenchmarkCaseEvaluationResult(BaseModel):
    sample_id: str
    group_id: str
    label: str
    attack_type: str
    expected_action: str
    predicted_action: str
    risk_score: float
    passed: bool
    error_type: Optional[str] = None  # false_positive, false_negative, under_block, over_block


class BenchmarkReportV2(BaseModel):
    benchmark_id: str = "gg_benchmark_v2"
    total_cases: int
    passed_cases: int
    accuracy: float
    precision: float
    recall: float
    macro_f1: float
    false_positive_rate: float
    under_block_rate: float
    over_block_rate: float
    by_attack_type: dict[str, dict[str, float]]
    by_language: dict[str, dict[str, float]]
    failure_cases: List[BenchmarkCaseEvaluationResult] = Field(default_factory=list)
