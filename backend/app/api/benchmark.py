import json
from pathlib import Path
from fastapi import APIRouter
from app.benchmark.schemas import BenchmarkReportV2
from app.benchmark.runner_v2 import run_benchmark_v2
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


@router.post("/run_v2", response_model=BenchmarkReportV2)
def execute_benchmark_v2():
    samples = generate_ielts_injected_samples(BASE_ESSAYS)
    return run_benchmark_v2(samples)
