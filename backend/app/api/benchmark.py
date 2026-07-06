import json
from pathlib import Path
from fastapi import APIRouter, HTTPException

from app.benchmark.failure_analysis import seeded_failure_analysis
from app.benchmark.runner_v2 import run_benchmark_v2
from app.benchmark.runner_v3 import run_benchmark_v3
from app.benchmark.schemas import BenchmarkReportV2
from app.benchmark.transforms.injectors import generate_ielts_injected_samples

router = APIRouter()

BASE_ESSAYS = [
    {
        "text": "Some people believe technology has made education more accessible than ever before. I partly agree because online resources allow students to study anywhere and at any time. However, technology also creates distractions. Many students spend too much time on social media instead of focusing on their lessons.",
        "band": 5.5,
    },
    {
        "text": "Global warming is one of the most serious challenges facing the world today. Human activities such as industrial emissions and deforestation contribute significantly to rising temperatures. To address this issue, governments should invest in renewable energy sources like solar and wind power.",
        "band": 6.5,
    },
    {
        "text": "In recent years, remote working has become increasingly popular across many industries. This trend offers flexibility and eliminates daily commutes for employees. On the other hand, it can lead to social isolation and difficulties in maintaining work-life balance.",
        "band": 7.0,
    },
]


def resolve_project_root() -> Path:
    current = Path(__file__).resolve().parent
    for _ in range(5):
        if (current / "datasets" / "processed").exists() or (current / "frontend").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent.parent.parent


@router.post("/run_v2", response_model=BenchmarkReportV2)
def execute_benchmark_v2():
    samples = generate_ielts_injected_samples(BASE_ESSAYS)
    return run_benchmark_v2(samples)


@router.post("/v3/run")
def execute_benchmark_v3():
    return run_benchmark_v3()


@router.get("/v3/report")
def get_benchmark_v3_report():
    root = resolve_project_root()
    report_file = root / "datasets" / "reports" / "v3" / "benchmark_v3_combined.json"

    if not report_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Benchmark v3 report not found. Run Benchmark v3 first.",
        )

    try:
        with report_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read benchmark v3 report: {str(e)}",
        )


@router.get("/v3/failure-analysis")
def get_failure_analysis():
    root = resolve_project_root()
    failure_file = root / "datasets" / "reports" / "v3" / "failure_analysis.jsonl"

    if not failure_file.exists():
        seeded = seeded_failure_analysis()
        return {
            "is_demo": True,
            "count": len(seeded),
            "note": "Demo failure analysis data (file missing, run Benchmark v3 first)",
            "failures": [s.model_dump() if hasattr(s, "model_dump") else s.dict() for s in seeded],
        }

    failures = []
    try:
        with failure_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                failures.append(json.loads(line))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read failure analysis JSONL: {str(e)}",
        )

    if not failures:
        seeded = seeded_failure_analysis()
        return {
            "is_demo": True,
            "count": len(seeded),
            "note": "Demo failure analysis data (empty file)",
            "failures": [s.model_dump() if hasattr(s, "model_dump") else s.dict() for s in seeded],
        }

    return {
        "is_demo": False,
        "count": len(failures),
        "note": "Real failure analysis from latest benchmark run",
        "failures": failures,
    }


@router.post("/multi-perspective/run")
def run_multi_perspective():
    from app.benchmark.multi_perspective import evaluate_multi_perspective_scenarios
    report = evaluate_multi_perspective_scenarios()
    return report.model_dump()


@router.get("/multi-perspective/report")
def get_multi_perspective_report():
    root = resolve_project_root()
    report_file = root / "datasets" / "reports" / "multi_perspective_report.json"

    if not report_file.exists():
        from app.benchmark.multi_perspective import evaluate_multi_perspective_scenarios
        report = evaluate_multi_perspective_scenarios()
        report_data = report.model_dump()
        report_data["is_demo"] = True
        return report_data

    try:
        with report_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read multi-perspective report: {str(e)}",
        )


@router.get("/decision-matrix")
def get_decision_matrix_endpoint():
    from app.benchmark.decision_matrix import get_decision_matrix
    return get_decision_matrix()


@router.post("/case-library/run")
def run_case_library_endpoint():
    from app.benchmark.case_library_runner import evaluate_case_library
    report = evaluate_case_library()
    return report.model_dump()


@router.get("/case-library")
def get_case_library_report():
    root = resolve_project_root()
    report_file = root / "datasets" / "reports" / "case_library_report.json"

    if not report_file.exists():
        from app.benchmark.case_library_runner import evaluate_case_library
        report = evaluate_case_library()
        report_data = report.model_dump()
        report_data["is_demo"] = True
        return report_data

    try:
        with report_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read case library report: {str(e)}",
        )

