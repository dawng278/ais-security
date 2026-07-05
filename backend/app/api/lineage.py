from fastapi import APIRouter
from app.datasets.lineage import DatasetLineageReport, get_lineage_report

router = APIRouter()


@router.get("/report", response_model=DatasetLineageReport)
def lineage_report():
    return get_lineage_report()
