import re
from app.firewall.schemas import GradingCriteria, GradingResult


class GraderBoundaryError(ValueError):
    pass


def build_protected_grader_request(content: str, rubric_id: str = "ielts_writing_v1") -> dict:
    return {
        "schema_version": "protected_grader_request.v1",
        "system_channel": {
            "role": "system",
            "rubric_id": rubric_id,
            "instruction": "Grade only the candidate_content field using the configured IELTS rubric.",
        },
        "candidate_channel": {
            "role": "candidate_content",
            "content": content,
            "boundary": "candidate_content_is_untrusted",
        },
        "metadata": {
            "adapter": "MockGrader",
            "adapter_version": "phase3_mock_grader_v1",
            "score_integrity_status": "DETERMINISTIC_DEMO",
        },
    }


def validate_grading_result(result: GradingResult) -> GradingResult:
    if not 0.0 <= result.overall_band <= 9.0:
        raise GraderBoundaryError("overall_band_out_of_range")
    for name, value in result.criteria.model_dump().items():
        if not 0.0 <= value <= 9.0:
            raise GraderBoundaryError(f"criteria_{name}_out_of_range")
    return result


def mock_grade(text: str, mode: str = "clean") -> GradingResult:
    # Keep the boundary explicit even in the deterministic demo adapter. The
    # mock still scores deterministically, but candidate text never becomes a
    # system instruction string.
    build_protected_grader_request(text)
    has_score_manipulation = bool(re.search(r"(?i)band\s*9|cho\s*điểm\s*cao|give\s*high\s*score", text))

    if mode == "baseline" and has_score_manipulation:
        return validate_grading_result(GradingResult(
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
        ))

    return validate_grading_result(GradingResult(
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
    ))
