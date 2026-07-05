from typing import Dict, List
from app.arena.schemas import AttackerProfile

ATTACKER_PROFILES: Dict[str, AttackerProfile] = {
    "novice_cheater": AttackerProfile(
        profile_id="novice_cheater",
        name="Novice Cheater",
        description="Naive student attempting basic direct prompt injection in English and Vietnamese.",
        skill_level="Novice",
        attack_types=["direct_english", "direct_vietnamese"],
    ),
    "multilingual_attacker": AttackerProfile(
        profile_id="multilingual_attacker",
        name="Multilingual Attacker",
        description="Cross-lingual attacker deploying score manipulation instructions in multiple languages.",
        skill_level="Intermediate",
        attack_types=["direct_vietnamese", "multilingual_score_manipulation", "direct_english"],
    ),
    "obfuscation_attacker": AttackerProfile(
        profile_id="obfuscation_attacker",
        name="Obfuscation Attacker",
        description="Advanced adversary using spacing, markdown spoofing, and evasion tricks to bypass keyword filters.",
        skill_level="Advanced",
        attack_types=["unicode_obfuscation", "markdown_role_spoofing", "unicode_obfuscation"],
    ),
    "adaptive_attacker": AttackerProfile(
        profile_id="adaptive_attacker",
        name="Adaptive Multi-Vector Attacker",
        description="Full multi-stage attacker executing direct injection, multilingual overrides, role spoofing, and character obfuscation.",
        skill_level="Expert",
        attack_types=[
            "direct_english",
            "direct_vietnamese",
            "unicode_obfuscation",
            "markdown_role_spoofing",
            "multilingual_score_manipulation",
        ],
    ),
}


def get_all_profiles() -> List[AttackerProfile]:
    return list(ATTACKER_PROFILES.values())


def get_profile_by_id(profile_id: str) -> AttackerProfile:
    return ATTACKER_PROFILES.get(profile_id, ATTACKER_PROFILES["adaptive_attacker"])
