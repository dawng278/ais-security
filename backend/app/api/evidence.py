import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.evidence.schemas import EvidenceReport


router = APIRouter()


def resolve_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "datasets").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent.parent


@router.get("/latest", response_model=EvidenceReport)
def get_latest_evidence():
    root = resolve_project_root()
    report_file = root / "datasets" / "reports" / "v3" / "evidence" / "evidence_report.json"

    if not report_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Evidence report not found. Run Benchmark v3 first.",
        )

    try:
        with report_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read evidence report: {str(e)}",
        )
