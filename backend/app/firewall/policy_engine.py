from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.firewall.schemas import FirewallAction, RiskLevel


OperatingMode = Literal["shadow", "warn", "enforce", "degraded"]

ACTION_ORDER: list[FirewallAction] = ["allow", "warn", "sanitize", "secure_grade", "manual_review", "block"]


@dataclass(frozen=True)
class PolicyDecision:
    selected_action: FirewallAction
    authoritative_action: FirewallAction
    risk_level: RiskLevel
    public_reason_code: str
    explanation_key: str
    policy_id: str = "static_phase3_policy"
    policy_version: str = "phase3_static_policy_v1"
    counterfactual_action: FirewallAction | None = None


def action_rank(action: FirewallAction) -> int:
    return ACTION_ORDER.index(action)


def stronger(action: FirewallAction, minimum: FirewallAction) -> FirewallAction:
    return action if action_rank(action) >= action_rank(minimum) else minimum


def risk_level_for_score(score: float) -> RiskLevel:
    if score >= 0.85:
        return "critical"
    if score >= 0.55:
        return "high"
    if score >= 0.25:
        return "medium"
    return "low"


def base_action_for_risk(score: float, categories: list[str], detector_unavailable: bool = False) -> FirewallAction:
    action: FirewallAction
    if score >= 0.90:
        action = "manual_review"
    elif score >= 0.55:
        action = "secure_grade"
    elif score >= 0.30:
        action = "warn"
    else:
        action = "allow"

    high_impact = {
        "evaluation_override",
        "multilingual_score_override",
        "instruction_override",
        "goal_hijacking",
        "delimiter_escape",
        "policy_bypass",
        "data_exfiltration",
        "prompt_extraction",
    }
    if any(category in high_impact for category in categories) and score >= 0.50:
        action = stronger(action, "secure_grade")
    if any(category in {"authority_claim", "delimiter_escape", "data_exfiltration", "policy_bypass"} for category in categories) and score >= 0.80:
        action = stronger(action, "manual_review")
    if detector_unavailable and score >= 0.50:
        action = stronger(action, "manual_review")
    return action


def evaluate_policy(
    *,
    risk_score: float,
    matched_categories: list[str],
    mode: OperatingMode = "enforce",
    detector_unavailable: bool = False,
) -> PolicyDecision:
    counterfactual = base_action_for_risk(
        risk_score,
        matched_categories,
        detector_unavailable=detector_unavailable,
    )
    authoritative: FirewallAction = counterfactual
    reason = "GG_REASON_POLICY_ALLOW"

    if mode == "shadow":
        authoritative = "allow"
        reason = "GG_REASON_SHADOW_COUNTERFACTUAL"
    elif mode == "warn":
        authoritative = "warn" if action_rank(counterfactual) >= action_rank("warn") else "allow"
        reason = "GG_REASON_WARN_MODE"
    elif mode == "degraded":
        if detector_unavailable and risk_score >= 0.30:
            authoritative = "manual_review"
            reason = "GG_REASON_DEGRADED_REVIEW"
        else:
            authoritative = "warn" if risk_score >= 0.25 else "allow"
            reason = "GG_REASON_DEGRADED_WARNING"
    elif counterfactual == "allow":
        reason = "GG_REASON_POLICY_ALLOW"
    elif counterfactual == "warn":
        reason = "GG_REASON_POLICY_WARN"
    elif counterfactual == "secure_grade":
        reason = "GG_REASON_SECURE_GRADE"
    elif counterfactual == "manual_review":
        reason = "GG_REASON_MANUAL_REVIEW"
    elif counterfactual == "block":
        reason = "GG_REASON_BLOCKED"

    return PolicyDecision(
        selected_action=counterfactual,
        authoritative_action=authoritative,
        risk_level=risk_level_for_score(risk_score),
        public_reason_code=reason,
        explanation_key=reason,
        counterfactual_action=counterfactual if authoritative != counterfactual else None,
    )
