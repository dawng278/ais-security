import random
from app.firewall.schemas import RedteamGenerateRequest, RedteamGenerateResponse
from app.redteam.attack_templates import ATTACK_TEMPLATES


def generate_attack(request: RedteamGenerateRequest) -> RedteamGenerateResponse:
    templates = ATTACK_TEMPLATES.get(request.attack_type)
    if not templates:
        templates = ATTACK_TEMPLATES["direct_vietnamese"]
        chosen_type = "direct_vietnamese"
    else:
        chosen_type = request.attack_type

    injected_span, explanation = random.choice(templates)
    injected_text = f"{request.text}{injected_span}"

    return RedteamGenerateResponse(
        attack_type=chosen_type,
        original_text=request.text,
        injected_text=injected_text,
        injected_span=injected_span.strip(),
        explanation=explanation,
    )
