from app.firewall.normalizer import normalize_text
from app.firewall.heuristics import detect_heuristics
from app.firewall.obfuscation import detect_obfuscation
from app.firewall.embedding_detector import compute_semantic_similarity
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

    return FirewallAnalyzeResponse(
        risk_score=risk_res.risk_score,
        risk_level=risk_res.risk_level,
        action=risk_res.action,
        attack_type=heur_res.attack_type,
        detected_patterns=patterns,
        normalization_flags=all_flags,
        explanation=risk_res.explanation,
    )
