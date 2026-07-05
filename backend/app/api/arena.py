from typing import List
from fastapi import APIRouter
from app.arena.attacker_profiles import get_all_profiles
from app.arena.scenario_runner import run_scenario
from app.arena.schemas import AttackerProfile, ArenaRunRequest, ArenaRunResponse

router = APIRouter()


@router.get("/profiles", response_model=List[AttackerProfile])
def get_profiles():
    return get_all_profiles()


@router.post("/run", response_model=ArenaRunResponse)
def run_attack_scenario(request: ArenaRunRequest):
    return run_scenario(request)
