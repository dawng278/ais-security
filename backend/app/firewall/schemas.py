from typing import Literal, Optional
from pydantic import BaseModel, Field


TaskType = Literal["writing", "speaking"]

RiskLevel = Literal["low", "medium", "high", "critical"]

FirewallAction = Literal[
    "allow",
    "warn",
    "secure_grade",
    "manual_review",
]

AttackType = Literal[
    "none",
    "direct_english",
    "direct_vietnamese",
    "direct_chinese",
    "unicode_obfuscation",
    "base64_instruction",
    "markdown_role_spoofing",
    "indirect_injection",
    "speaking_transcript_injection",
    "multilingual_score_manipulation",
    "unknown",
]


class FirewallAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    task_type: TaskType = "writing"


class FirewallAnalyzeResponse(BaseModel):
    risk_score: float
    risk_level: RiskLevel
    action: FirewallAction
    attack_type: AttackType
    detected_patterns: list[str] = []
    normalization_flags: list[str] = []
    explanation: str


class RedteamGenerateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    task_type: TaskType = "writing"
    attack_type: AttackType = "direct_vietnamese"


class RedteamGenerateResponse(BaseModel):
    attack_type: AttackType
    original_text: str
    injected_text: str
    injected_span: str
    explanation: str


class GradingCriteria(BaseModel):
    task_response: float
    coherence_cohesion: float
    lexical_resource: float
    grammar: float


class GradingResult(BaseModel):
    mode: Literal["baseline", "secure", "clean"]
    overall_band: float
    criteria: GradingCriteria
    feedback: str
    security_notes: Optional[str] = None


class SanitizerResult(BaseModel):
    cleaned_text: str
    removed_spans: list[str] = []


class VerifierResult(BaseModel):
    integrity_status: Literal["clean", "vulnerable", "protected", "needs_review"]
    attack_inflation: float = 0.0
    defense_recovery: float = 0.0
    score_stability: float = 0.0
    issues: list[str] = []
    recommendation: str


class SecureGradeResponse(BaseModel):
    firewall: FirewallAnalyzeResponse
    sanitizer: SanitizerResult
    grading: GradingResult
    verifier: VerifierResult


class CompareRequest(BaseModel):
    original_text: str
    injected_text: str
    task_type: TaskType = "writing"


class ScoreDelta(BaseModel):
    attack_inflation: float
    defense_recovery: float
    score_stability: float


class CompareResponse(BaseModel):
    clean_result: GradingResult
    baseline_injected_result: GradingResult
    secure_injected_result: GradingResult
    score_delta: ScoreDelta
    firewall: FirewallAnalyzeResponse
    verifier: VerifierResult


class DashboardStats(BaseModel):
    total_submissions: int
    attacks_detected: int
    high_risk_count: int
    average_risk_score: float
    score_manipulations_prevented: int
    attack_type_breakdown: dict[str, int]
    action_breakdown: dict[str, int]


class SecurityEvent(BaseModel):
    id: str
    submission_id: str
    risk_score: float
    risk_level: RiskLevel
    action: FirewallAction
    attack_type: AttackType
    detected_patterns: list[str]
    removed_spans: list[str]
    explanation: str
    created_at: str
