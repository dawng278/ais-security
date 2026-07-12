from app.firewall.normalizer import normalize_text
from app.firewall.heuristics import detect_heuristics
from app.firewall.obfuscation import detect_obfuscation
from app.firewall.embedding_detector import compute_semantic_similarity
from app.firewall.policy_engine import evaluate_policy
from app.firewall.risk_engine import compute_risk
from app.firewall.schemas import FirewallAnalyzeRequest, FirewallAnalyzeResponse


def analyze_submission(request: FirewallAnalyzeRequest) -> FirewallAnalyzeResponse:
    norm_res = normalize_text(request.text)
    heur_res = detect_heuristics(norm_res.normalized_text)
    obf_res = detect_obfuscation(norm_res.normalized_text, norm_res.flags)
    
    # Semantic embedding similarity evaluation
    semantic_score, matched_proto = compute_semantic_similarity(norm_res.normalized_text)
    
    risk_res = compute_risk(
        heuristic_score=heur_res.heuristic_score,
        obfuscation_score=obf_res.obfuscation_score,
        semantic_score=semantic_score,
        matched_categories=heur_res.matched_categories,
    )

    all_flags = list(set(norm_res.flags + obf_res.obfuscation_flags))
    patterns = list(heur_res.matched_patterns)
    if matched_proto and semantic_score >= 0.7:
        patterns.append(f"semantic_prototype_match: {matched_proto[:30]}...")

    detector_contributions = [
        {
            "detector_id": "heuristic_rules",
            "detector_version": "phase3_rules_v1",
            "runtime_health": "healthy",
            "score_contribution": heur_res.heuristic_score,
            "confidence": heur_res.heuristic_score,
            "technique_ids": list(heur_res.matched_categories),
            "evidence_spans": [],
            "latency_ms": 0,
            "warnings": [],
            "error_reason": "",
        },
        {
            "detector_id": "obfuscation_detector",
            "detector_version": "phase3_obfuscation_v1",
            "runtime_health": "healthy",
            "score_contribution": obf_res.obfuscation_score,
            "confidence": obf_res.obfuscation_score,
            "technique_ids": list(obf_res.obfuscation_flags),
            "evidence_spans": [],
            "latency_ms": 0,
            "warnings": [],
            "error_reason": "",
        },
        {
            "detector_id": "semantic_embedding",
            "detector_version": "phase3_embedding_contract_v1",
            "runtime_health": "unavailable" if semantic_score <= 0.1 and not matched_proto else "healthy",
            "score_contribution": semantic_score,
            "confidence": semantic_score,
            "technique_ids": [matched_proto] if matched_proto else [],
            "evidence_spans": [],
            "latency_ms": 0,
            "warnings": ["embedding may be fallback keyword mode"],
            "error_reason": "",
        },
    ]
    policy = evaluate_policy(
        risk_score=risk_res.risk_score,
        matched_categories=list(heur_res.matched_categories),
        mode="enforce",
        detector_unavailable=False,
    )

    return FirewallAnalyzeResponse(
        risk_score=risk_res.risk_score,
        risk_level=policy.risk_level,
        action=policy.authoritative_action,
        attack_type=heur_res.attack_type,
        detected_patterns=patterns,
        normalization_flags=all_flags,
        explanation=risk_res.explanation,
        detector_contributions=detector_contributions,
        public_reason_code=policy.public_reason_code,
        operating_mode="enforce",
        counterfactual_action=policy.counterfactual_action,
    )
