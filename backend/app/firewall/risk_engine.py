from dataclasses import dataclass
from app.firewall.schemas import FirewallAction, RiskLevel


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
) -> RiskEvaluationResult:
    risk_score = (
        0.50 * heuristic_score +
        0.20 * obfuscation_score +
        0.15 * semantic_score +
        0.15 * classifier_score
    )
    risk_score = round(min(max(risk_score, 0.0), 1.0), 2)

    if risk_score >= 0.85:
        risk_level: RiskLevel = "critical"
        action: FirewallAction = "manual_review"
        explanation = "High-severity prompt injection or score manipulation detected."
    elif risk_score >= 0.65:
        risk_level: RiskLevel = "high"
        action: FirewallAction = "secure_grade"
        explanation = "Suspicious instructions detected. Secure grading mode and sanitization recommended."
    elif risk_score >= 0.35:
        risk_level: RiskLevel = "medium"
        action: FirewallAction = "warn"
        explanation = "Mild risk or obfuscated patterns detected. Sanitization applied before grading."
    else:
        risk_level: RiskLevel = "low"
        action: FirewallAction = "allow"
        explanation = "No significant security threat detected in user submission."

    return RiskEvaluationResult(
        risk_score=risk_score,
        risk_level=risk_level,
        action=action,
        explanation=explanation,
    )
