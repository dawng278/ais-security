from fastapi import APIRouter
from app.firewall.schemas import RedteamGenerateRequest, RedteamGenerateResponse
from app.redteam.generator import generate_attack

router = APIRouter()


@router.post("/generate", response_model=RedteamGenerateResponse)
def generate(request: RedteamGenerateRequest):
    return generate_attack(request)
