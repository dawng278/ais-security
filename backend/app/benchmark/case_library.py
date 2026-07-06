from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class StakeholderImpact(BaseModel):
    stakeholder: str
    concern: str
    risk_if_wrong: str


class DecisionRationale(BaseModel):
    expected_action: str
    reason: str
    under_block_risk: str
    over_block_risk: str
    evidence_required: List[str] = Field(default_factory=list)


class ScenarioCase(BaseModel):
    case_id: str
    title: str
    scenario_group: str
    task_type: str = "writing"
    language: str = "en"
    text: str
    is_attack: bool = True
    expected_action: str
    expected_score_behavior: str
    primary_perspective: str
    secondary_perspectives: List[str] = Field(default_factory=list)
    risk_dimension: str
    stakeholder_lenses: List[str] = Field(default_factory=list)
    stakeholder_impacts: List[StakeholderImpact] = Field(default_factory=list)
    decision_rationale: DecisionRationale
    tags: List[str] = Field(default_factory=list)


class CaseLibrarySummary(BaseModel):
    total_cases: int
    by_scenario_group: Dict[str, int]
    by_language: Dict[str, int]
    by_expected_action: Dict[str, int]
    by_primary_perspective: Dict[str, int]
    cases: List[ScenarioCase] = Field(default_factory=list)
