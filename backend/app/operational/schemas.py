from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.config import settings
from app.firewall.schemas import FirewallAction


OperatingMode = Literal["shadow", "warn", "enforce", "degraded"]
ReviewState = Literal["pending", "assigned", "in_review", "resolved_allow", "resolved_block", "escalated", "expired"]
PolicyState = Literal["draft", "validated", "published", "superseded", "rolled_back", "archived"]


class GatewayRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["grading_request.v1"] = "grading_request.v1"
    request_id: str = Field(..., min_length=4, max_length=96, pattern=r"^[A-Za-z0-9_.:-]+$")
    correlation_id: str | None = Field(default=None, max_length=96)
    submission_id: str = Field(..., min_length=1, max_length=128)
    pseudonymous_user_id: str | None = Field(default=None, max_length=128)
    task_type: Literal["writing", "speaking"] = "writing"
    candidate_content: str = Field(..., min_length=1)
    language: str = Field(default="en", min_length=2, max_length=16, pattern=r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})?$")
    grader_context: dict[str, Any] = Field(default_factory=dict)
    timeout_budget_ms: int = Field(default=3000, ge=100, le=10000)
    metadata: dict[str, str] = Field(default_factory=dict)

    @field_validator("candidate_content")
    @classmethod
    def candidate_content_size(cls, value: str) -> str:
        if len(value) > settings.max_candidate_content_chars:
            raise ValueError("candidate_content_too_large")
        return value

    @field_validator("metadata")
    @classmethod
    def metadata_allowlist(cls, value: dict[str, str]) -> dict[str, str]:
        allowed = {"source", "fixture", "client_version", "environment", "content_hash"}
        unknown = set(value) - allowed
        if unknown:
            raise ValueError(f"metadata_keys_not_allowed:{sorted(unknown)}")
        for item in value.values():
            if len(str(item)) > 256:
                raise ValueError("metadata_value_too_large")
        return value


class GatewayDecisionResponse(BaseModel):
    schema_version: Literal["grading_decision.v1"] = "grading_decision.v1"
    decision_id: str
    request_id: str
    correlation_id: str
    operating_mode: OperatingMode
    applied_action: FirewallAction
    counterfactual_action: FirewallAction | None = None
    risk_score: float
    severity: str
    detected_techniques: list[str]
    policy_id: str
    policy_version: str
    detector_health: dict[str, str]
    review_state: ReviewState | None = None
    incident_id: str | None = None
    review_id: str | None = None
    final_outcome: str
    grader_result_metadata: dict[str, Any] = Field(default_factory=dict)
    safe_preview: str
    redaction_state: str
    retryable: bool = False
    created_at: str
    completed_at: str


class AssignReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assignee: str = Field(..., min_length=2, max_length=128)
    expected_version: int = Field(..., ge=1)
    note: str | None = Field(default=None, max_length=1000)


class ResolveReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resolution: Literal["resolved_allow", "resolved_block", "escalated"]
    expected_version: int = Field(..., ge=1)
    note: str = Field(..., min_length=2, max_length=1000)
    confirm: bool = True


class StartReviewRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(..., ge=1)
    note: str | None = Field(default=None, max_length=1000)


class DevSessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    subject: str = Field(default="phase5-demo-analyst", min_length=2, max_length=128)
    client_id: str = Field(default="phase5-console", min_length=2, max_length=128)
    roles: list[str] = Field(default_factory=lambda: ["viewer", "analyst", "policy_manager", "security_admin", "integration_service"])


class PolicyDraftRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    policy_id: str = Field(..., min_length=3, max_length=96, pattern=r"^[A-Za-z0-9_.:-]+$")
    name: str = Field(..., min_length=3, max_length=160)
    version: str = Field(..., min_length=1, max_length=64)
    policy: dict[str, Any]


class PolicyPublishRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version_id: str
    confirm: bool = True


class PolicyRollbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    target_version_id: str
    confirm: bool = True


class ModeChangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: OperatingMode
    expected_version: int = Field(..., ge=1)
    justification: str = Field(..., min_length=4, max_length=500)
    confirm: bool = True
