from app.firewall.normalizer import normalize_text
from app.firewall.heuristics import detect_heuristics
from app.firewall.obfuscation import detect_obfuscation
from app.firewall.risk_engine import compute_risk
from app.firewall.schemas import FirewallAnalyzeRequest, FirewallAnalyzeResponse


def analyze_submission(request: FirewallAnalyzeRequest) -> FirewallAnalyzeResponse:
    norm_res = normalize_text(request.text)
    heur_res = detect_heuristics(norm_res.normalized_text)
    obf_res = detect_obfuscation(norm_res.normalized_text, norm_res.flags)
    risk_res = compute_risk(heur_res.heuristic_score, obf_res.obfuscation_score)

    all_flags = list(set(norm_res.flags + obf_res.obfuscation_flags))

    return FirewallAnalyzeResponse(
        risk_score=risk_res.risk_score,
        risk_level=risk_res.risk_level,
        action=risk_res.action,
        attack_type=heur_res.attack_type,
        detected_patterns=heur_res.matched_patterns,
        normalization_flags=all_flags,
        explanation=risk_res.explanation,
    )
