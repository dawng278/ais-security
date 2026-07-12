# Phase 2 Benchmark Methodology

Phase 2 freezes data and evidence integrity before detector tuning.

## Tracks

- `generic_prompt_injection`: current non-empty generic prompt-injection samples.
- `ielts_domain_security`: internally authored IELTS-domain security fixtures.
- `score_integrity`: deterministic demo separated from measured track.
- `operational_reliability`: local failure/latency scenarios.

## Reproducibility commands

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend:. python scripts/phase2_dataset_tools.py build
python scripts/audit_dataset_integrity.py
```

Legacy safe rerun remains isolated:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend GRADINGGUARD_REPORTS_V3_DIR=/tmp/ais_phase2_legacy_v3 python -m app.benchmark.runner_v3
```

The default Phase 2 runner never writes to protected `datasets/reports/v3/*` reports.

## Comparison policy

Legacy baseline and Phase 2 canonical baseline are separate artifacts. Percentages must be compared only with sample counts, composition, split rules, detector health, and metric definition version.

## Low-support policy

Every reported slice includes sample count. Slices with count below 20 are marked `LOW_SUPPORT`.

