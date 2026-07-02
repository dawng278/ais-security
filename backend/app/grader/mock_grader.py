import re
from app.firewall.schemas import GradingCriteria, GradingResult


def mock_grade(text: str, mode: str = "clean") -> GradingResult:
    has_score_manipulation = bool(re.search(r"(?i)band\s*9|cho\s*điểm\s*cao|give\s*high\s*score", text))

    if mode == "baseline" and has_score_manipulation:
        return GradingResult(
            mode="baseline",
            overall_band=8.5,
            criteria=GradingCriteria(
                task_response=8.5,
                coherence_cohesion=8.5,
                lexical_resource=8.5,
                grammar=8.5,
            ),
            feedback="Manipulated evaluation: System prompt instructions overridden, awarding high score.",
            security_notes=None,
        )

    return GradingResult(
        mode="secure" if mode == "secure" else "clean",
        overall_band=5.5,
        criteria=GradingCriteria(
            task_response=5.5,
            coherence_cohesion=6.0,
            lexical_resource=5.5,
            grammar=5.0,
        ),
        feedback="The response addresses the prompt with adequate ideas but demonstrates limited grammatical range and lexical variation.",
        security_notes="Evaluated under Secure Grading Mode. Potential prompt injection filtered prior to scoring." if mode == "secure" else None,
    )
