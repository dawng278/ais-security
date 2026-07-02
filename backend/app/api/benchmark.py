import json
from pathlib import Path
from fastapi import APIRouter
from app.benchmark.runner import BenchmarkCase, BenchmarkSummary, run_benchmark

router = APIRouter()


@router.post("/run", response_model=BenchmarkSummary)
def execute_benchmark():
    dataset_path = Path(__file__).parent.parent.parent / "datasets" / "benchmark_v1.jsonl"
    cases: list[BenchmarkCase] = []

    if dataset_path.exists():
        with open(dataset_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    cases.append(BenchmarkCase(**data))

    return run_benchmark(cases)
