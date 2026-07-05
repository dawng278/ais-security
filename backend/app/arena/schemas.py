from typing import List
from pydantic import BaseModel


class AttackerProfile(BaseModel):
    profile_id: str
    name: str
    description: str
    skill_level: str
    attack_types: List[str]


class DefenseStep(BaseModel):
    name: str
    status: str
    details: str


class ArenaAttempt(BaseModel):
    attempt_id: int
    attack_type: str
    injected_span: str
    baseline_score: float
    secure_score: float
    risk_score: float
    action: str
    result_status: str
    removed_spans: List[str]
    defense_steps: List[DefenseStep]


class ArenaRunRequest(BaseModel):
    original_text: str
    profile_id: str = "adaptive_attacker"
    task_type: str = "writing"


class ArenaRunResponse(BaseModel):
    scenario_id: str
    profile: AttackerProfile
    attempts: List[ArenaAttempt]
    total_attempts: int
    secured_attempts: int
    manual_review_attempts: int
    benign_allowed: int
    total_score_inflation_prevented: float
    clean_utility_loss: float
