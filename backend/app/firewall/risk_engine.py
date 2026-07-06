from dataclasses import dataclass
from typing import Optional
from app.firewall.schemas import FirewallAction, RiskLevel

ACTION_RANK: dict[str, int] = {
    "allow": 0,
    "warn": 1,
    "secure_grade": 2,
    "manual_review": 3,
}

RANK_TO_ACTION: dict[int, FirewallAction] = {
    0: "allow",
    1: "warn",
    2: "secure_grade",
    3: "manual_review",
}


@dataclass
class RiskEvaluationResult:
    risk_score: float
    risk_level: RiskLevel
    action: FirewallAction
    explanation: str


def compute_risk(
    heuristic_score: float,
    obfuscation_score: float,
    semantic_score: float = 0.0,
    classifier_score: float = 0.0,
    matched_categories: Optional[list[str]] = None,
) -> RiskEvaluationResult:
    categories = matched_categories or []

    risk_score = (
        0.50 * heuristic_score +
        0.20 * obfuscation_score +
        0.15 * semantic_score +
        0.15 * classifier_score
    )
    risk_score = round(min(max(risk_score, 0.0), 1.0), 2)

    # Boost risk score when high-confidence heuristic rules trigger
    if heuristic_score >= 0.90:
        risk_score = max(risk_score, round(min(0.85 + 0.15 * (heuristic_score - 0.90), 0.98), 2))
    elif heuristic_score >= 0.70:
        risk_score = max(risk_score, round(min(0.65 + 0.20 * (heuristic_score - 0.70), 0.85), 2))

    if risk_score >= 0.85:
        risk_level: RiskLevel = "critical"
        action: FirewallAction = "manual_review"
        explanation = "High-severity prompt injection or score manipulation detected."
    elif risk_score >= 0.45:
        risk_level: RiskLevel = "high"
        action: FirewallAction = "secure_grade"
        explanation = "Suspicious instructions detected. Secure grading mode and sanitization recommended."
    elif risk_score >= 0.25:
        risk_level: RiskLevel = "medium"
        action: FirewallAction = "warn"
        explanation = "Mild risk or obfuscated patterns detected. Sanitization applied before grading."
    else:
        risk_level: RiskLevel = "low"
        action: FirewallAction = "allow"
        explanation = "No significant security threat detected in user submission."

    # Policy Override Rules for High-Risk Categories
    high_risk_categories = {
        "evaluation_override",
        "multilingual_score_override",
        "instruction_override",
        "goal_hijacking",
        "delimiter_escape",
    }
    
    current_rank = ACTION_RANK.get(action, 0)

    # 1. Enforce secure_grade minimum for explicit score manipulation or instruction overrides
    if any(cat in categories for cat in high_risk_categories) and heuristic_score >= 0.65:
        current_rank = max(current_rank, ACTION_RANK["secure_grade"])
        explanation = "High-confidence score manipulation or instruction override detected. Secure grading enforced."

    # 2. Escalate role spoofing + high risk or delimiter escape + high risk to manual_review
    if ("authority_claim" in categories or "delimiter_escape" in categories) and risk_score >= 0.80:
        current_rank = max(current_rank, ACTION_RANK["manual_review"])
        explanation = "Role spoofing or tag breakout attempt with high risk. Manual review required."

    action = RANK_TO_ACTION[current_rank]

    # Recalculate risk_level according to final action
    if action == "manual_review":
        risk_level = "critical"
    elif action == "secure_grade":
        risk_level = "high"
    elif action == "warn":
        risk_level = "medium"
    else:
        risk_level = "low"

    return RiskEvaluationResult(
        risk_score=risk_score,
        risk_level=risk_level,
        action=action,
        explanation=explanation,
    )
