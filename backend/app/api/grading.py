from fastapi import APIRouter
from app.firewall.schemas import (
    CompareRequest,
    CompareResponse,
    FirewallAnalyzeRequest,
    GradingResult,
    SecureGradeResponse,
)
from app.firewall.service import analyze_submission
from app.firewall.sanitizer import sanitize_text
from app.firewall.verifier import verify_scores
from app.grader.mock_grader import mock_grade

router = APIRouter()


@router.post("/baseline", response_model=GradingResult)
def grade_baseline(request: FirewallAnalyzeRequest):
    return mock_grade(request.text, mode="baseline")


@router.post("/secure", response_model=SecureGradeResponse)
def grade_secure(request: FirewallAnalyzeRequest):
    firewall_res = analyze_submission(request)
    sanitizer_res = sanitize_text(request.text)
    grading_res = mock_grade(sanitizer_res.cleaned_text, mode="secure")
    clean_baseline_res = mock_grade(sanitizer_res.cleaned_text, mode="clean")
    baseline_injected_res = mock_grade(request.text, mode="baseline")
    verifier_res = verify_scores(clean_baseline_res, baseline_injected_res, grading_res)

    return SecureGradeResponse(
        firewall=firewall_res,
        sanitizer=sanitizer_res,
        grading=grading_res,
        verifier=verifier_res,
    )


@router.post("/compare", response_model=CompareResponse)
def compare(request: CompareRequest):
    clean_res = mock_grade(request.original_text, mode="clean")
    baseline_inj_res = mock_grade(request.injected_text, mode="baseline")
    
    fw_req = FirewallAnalyzeRequest(text=request.injected_text, task_type=request.task_type)
    firewall_res = analyze_submission(fw_req)
    sanitizer_res = sanitize_text(request.injected_text)
    secure_inj_res = mock_grade(sanitizer_res.cleaned_text, mode="secure")
    
    verifier_res = verify_scores(clean_res, baseline_inj_res, secure_inj_res)

    return CompareResponse(
        clean_result=clean_res,
        baseline_injected_result=baseline_inj_res,
        secure_injected_result=secure_inj_res,
        score_delta={
            "attack_inflation": verifier_res.attack_inflation,
            "defense_recovery": verifier_res.defense_recovery,
            "score_stability": verifier_res.score_stability,
        },
        firewall=firewall_res,
        verifier=verifier_res,
    )
