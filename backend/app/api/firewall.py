from fastapi import APIRouter
from app.firewall.schemas import FirewallAnalyzeRequest, FirewallAnalyzeResponse
from app.firewall.service import analyze_submission

router = APIRouter()


@router.post("/analyze", response_model=FirewallAnalyzeResponse)
def analyze(request: FirewallAnalyzeRequest):
    return analyze_submission(request)
