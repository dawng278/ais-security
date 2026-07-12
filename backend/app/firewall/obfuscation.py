import re
from dataclasses import dataclass


SPACED_IGNORE_RE = re.compile(r"i\s*g\s*n\s*o\s*r\s*e", re.IGNORECASE)
SPACED_SYSTEM_RE = re.compile(r"s\s*y\s*s\s*t\s*e\s*m\s*:", re.IGNORECASE)
SYMBOL_HEAVY_RE = re.compile(r"[#*_`~>\[\]{}|]{6,}")


@dataclass
class ObfuscationResult:
    obfuscation_score: float
    obfuscation_flags: list[str]


def detect_obfuscation(
    normalized_text: str,
    normalization_flags: list[str],
) -> ObfuscationResult:
    flags: list[str] = []
    score = 0.0

    if SPACED_IGNORE_RE.search(normalized_text):
        flags.append("spaced_ignore_detected")
        score = max(score, 0.75)

    if SPACED_SYSTEM_RE.search(normalized_text):
        flags.append("spaced_role_spoofing_detected")
        score = max(score, 0.75)

    if "base64_like_payload_detected" in normalization_flags:
        flags.append("base64_like_payload_detected")
        score = max(score, 0.70)

    if "url_encoded_payload_detected" in normalization_flags:
        flags.append("url_encoded_payload_detected")
        score = max(score, 0.65)

    if "markdown_or_code_block_detected" in normalization_flags:
        flags.append("markdown_or_code_block_detected")
        score = max(score, 0.45)

    if "zero_width_removed" in normalization_flags:
        flags.append("zero_width_obfuscation_detected")
        score = max(score, 0.55)

    if "bidi_control_removed" in normalization_flags:
        flags.append("bidi_control_obfuscation_detected")
        score = max(score, 0.55)

    if SYMBOL_HEAVY_RE.search(normalized_text):
        flags.append("symbol_heavy_payload_detected")
        score = max(score, 0.35)

    return ObfuscationResult(
        obfuscation_score=min(score, 1.0),
        obfuscation_flags=flags,
    )
