from typing import List
from pydantic import BaseModel, Field


class StakeholderLens(BaseModel):
    stakeholder_id: str
    name: str
    main_concern: str
    what_good_looks_like: str
    risk_if_underblocked: str
    risk_if_overblocked: str
    evidence_needed: List[str] = Field(default_factory=list)


class StakeholderDecisionView(BaseModel):
    case_id: str
    stakeholder_id: str
    stakeholder_name: str
    expected_action: str
    decision_rationale: str
    underblock_impact: str
    overblock_impact: str
    evidence_needed: List[str] = Field(default_factory=list)


STAKEHOLDER_LENSES: List[StakeholderLens] = [
    StakeholderLens(
        stakeholder_id="student",
        name="Student / Test-taker",
        main_concern="Fairness and not being penalized for benign writing.",
        what_good_looks_like="Clean essays and academic discussion are not overblocked.",
        risk_if_underblocked="Dishonest students may gain unfair score inflation.",
        risk_if_overblocked="Honest students may be unfairly flagged or lose valid content.",
        evidence_needed=["removed_spans", "risk_score", "secure_score", "clean_utility_loss"],
    ),
    StakeholderLens(
        stakeholder_id="examiner",
        name="IELTS Examiner / Rubric Owner",
        main_concern="Rubric integrity and score consistency.",
        what_good_looks_like="The final band score follows the rubric, not injected instructions.",
        risk_if_underblocked="The rubric can be bypassed by student-written commands.",
        risk_if_overblocked="Legitimate essay content may be removed before grading.",
        evidence_needed=["rubric_score", "sanitized_text", "score_stability"],
    ),
    StakeholderLens(
        stakeholder_id="platform_operator",
        name="Platform Operator",
        main_concern="Reliable, low-friction grading workflow.",
        what_good_looks_like="Most cases are handled automatically; uncertain cases go to review.",
        risk_if_underblocked="Manipulated scores damage platform trust.",
        risk_if_overblocked="Too many manual reviews increase operational cost.",
        evidence_needed=["action", "manual_review_rate", "latency_ms"],
    ),
    StakeholderLens(
        stakeholder_id="security_analyst",
        name="Security Analyst",
        main_concern="Detecting prompt injection, role spoofing, obfuscation, and bypass attempts.",
        what_good_looks_like="High-risk attacks trigger secure_grade or manual_review.",
        risk_if_underblocked="Attack payload reaches the grader.",
        risk_if_overblocked="Rules become too broad and create noisy alerts.",
        evidence_needed=["detected_patterns", "attack_type", "risk_score", "failure_type"],
    ),
    StakeholderLens(
        stakeholder_id="education_institution",
        name="Education Institution",
        main_concern="Trust, fairness, and defensibility of automated grading.",
        what_good_looks_like="Scores are protected and decisions can be explained.",
        risk_if_underblocked="Certificate or placement decisions become unreliable.",
        risk_if_overblocked="Students may appeal due to unfair automated decisions.",
        evidence_needed=["evidence_report", "score_integrity_metrics", "audit_notes"],
    ),
    StakeholderLens(
        stakeholder_id="auditor",
        name="Auditor / External Reviewer",
        main_concern="Reproducibility and evidence.",
        what_good_looks_like="Dataset hash, config hash, benchmark report, and failure analysis are available.",
        risk_if_underblocked="Security claims cannot be trusted.",
        risk_if_overblocked="Fairness claims cannot be trusted.",
        evidence_needed=["dataset_sha256", "config_sha256", "git_commit", "failure_analysis"],
    ),
    StakeholderLens(
        stakeholder_id="research_team",
        name="Research / Improvement Team",
        main_concern="Learning from failures and improving the detector.",
        what_good_looks_like="Failures are categorized into actionable next fixes.",
        risk_if_underblocked="Missed attack families remain unknown.",
        risk_if_overblocked="Hard-negative weaknesses remain hidden.",
        evidence_needed=["failure_breakdown", "representative_examples", "next_fix"],
    ),
]


def get_stakeholder_lenses() -> List[StakeholderLens]:
    return STAKEHOLDER_LENSES
