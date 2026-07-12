# Phase 0 Repository Truth Audit

Status: PARTIAL

Date: 2026-07-13

Repository: `/home/dawngbeo/school-project/ais-gau-security`

Reference repository, read-only: `/home/dawngbeo/Documents/github-project/gau-ielts`

## Repository State

- Branch: `main`
- HEAD: `424f6e1f65d7613d9fbdcdf96bbd6541ff9f512d`
- Remote: `origin https://github.com/dawng278/ais-security.git`
- Stash: empty

Existing dirty files, classified as `USER_EXISTING_WORK`:

- `datasets/reports/v3/benchmark_v3_combined.json`
- `datasets/reports/v3/evidence/evidence_card.md`
- `datasets/reports/v3/evidence/evidence_report.json`

The dirty diff only updates evidence run metadata from:

- `run_20260706_083159_903f0a`, commit `9d8417d`

to:

- `run_20260710_134918_92b700`, commit `424f6e1`

These files were not regenerated or overwritten during this audit.

## GAU IELTS Reference State

Before any design reference work, the GAU IELTS repository was recorded as dirty with existing Reading-related changes. HEAD:

```text
f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7
```

No file in the GAU IELTS repository was edited by this audit.

## Inventory

Backend:

- FastAPI app in `backend/app/main.py`
- Routers: firewall, redteam, grading, dashboard, benchmark, arena, evidence, lineage
- Tests: `backend/tests/*.py`
- Runtime requirements: `backend/requirements.txt`

Frontend:

- Next.js 16 app in `frontend/src/app`
- Existing pages: `/`, `/dashboard`, `/judge-view`, `/playground`, `/attack-arena`, `/benchmark`, `/data-lineage`
- No frontend `/evidence` route exists at audit time.

Data and evidence:

- Canonical processed dataset: `datasets/processed/canonical_prompt_injection.jsonl`
- Existing v3 reports: `datasets/reports/v3/*`
- Existing evidence card/report: `datasets/reports/v3/evidence/*`
- Source registry: `datasets/registry/sources.yaml`
- License registry: `datasets/registry/licenses.md`

Deployment:

- No `Dockerfile`, `docker-compose.yml`, or `.dockerignore` was found in the repo root or project tree at audit time.
- README currently claims Docker Compose support.

## Baseline Verification

Backend tests:

```bash
PYTHONPATH=backend python -m pytest backend/tests -q
```

Result:

```text
30 passed in 0.27s
```

The README-level command without `PYTHONPATH` failed with `ModuleNotFoundError: No module named 'app'`.

Frontend lint:

```bash
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/eslint
```

Result: FAIL.

Representative failures:

- `@typescript-eslint/no-explicit-any` in `attack-arena`, `benchmark`, `judge-view`, `api.ts`, `types.ts`
- `react-hooks/set-state-in-effect` in `benchmark/page.tsx` and `data-lineage/page.tsx`
- `react/no-unescaped-entities` in `attack-arena/page.tsx`

Frontend build:

```bash
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/next build
```

Result: PASS.

Built routes:

```text
/
/_not-found
/attack-arena
/benchmark
/dashboard
/data-lineage
/judge-view
/playground
```

API route smoke:

```text
GET  /health                              200
GET  /api/dashboard/stats                 200
GET  /api/benchmark/v3/report             200
GET  /api/benchmark/v3/failure-analysis   200
GET  /api/lineage/report                  200
GET  /api/evidence/latest                 200
POST /api/firewall/analyze                200
```

Importing the backend emitted:

```text
Warning: sentence-transformers or numpy not available (No module named 'sentence_transformers'). Embedding detector running in fallback mode.
```

Benchmark v3 safe rerun:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend GRADINGGUARD_REPORTS_V3_DIR=/tmp/ais_gau_security_phase0_benchmark python -m app.benchmark.runner_v3
```

Result:

```text
Total Cases: 662
Accuracy: 79.0%
Failure Cases Analyzed: 139
Outputs saved to /tmp/ais_gau_security_phase0_benchmark
```

Generated temporary evidence:

```text
run_id: run_20260712_185142_d55d54
git_commit: 8c91f2d
```

The safe rerun used an output directory override and did not overwrite existing tracked report files.

## Existing Evidence Snapshot

From `datasets/reports/v3/benchmark_v3_combined.json`:

```text
benchmark_id: gg_benchmark_v3
total_cases: 662
accuracy: 0.79
precision: 1.0
recall: 0.47
macro_f1: 0.64
false_positive_rate: 0.0
under_block_rate: 0.21
failure_analysis_count: 139
```

From `datasets/reports/v3/evidence/evidence_report.json`:

```text
run_id: run_20260710_134918_92b700
git_commit: 424f6e1
dataset_total: 965
detector_version: ensemble_v3
enable_embedding_detector: true
```

Evidence inconsistency:

- Runtime says embedding detector is in fallback mode.
- Evidence says `enable_embedding_detector: true`.
- This was fixed for newly generated evidence after this audit by recording embedding dependency, model load, runtime state, and fallback reason.
- Existing tracked evidence artifacts were not regenerated because they are dirty user work.

Embedding evidence verification after the fix:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend GRADINGGUARD_REPORTS_V3_DIR=/tmp/ais_gau_security_embedding_evidence python -m app.benchmark.runner_v3
```

Generated detector snapshot:

```text
enable_embedding_detector: false
embedding_configured_state: enabled
embedding_dependency_state: missing
embedding_model_load_state: not_attempted
embedding_runtime_state: unavailable
embedding_model_name: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
embedding_fallback_reason: No module named 'sentence_transformers'
```

## Dataset Snapshot

Line counts observed:

```text
datasets/processed/canonical_prompt_injection.jsonl      965
datasets/benchmark_v1.jsonl                                5
datasets/raw/deepset_prompt_injections/train.csv         563
datasets/raw/deepset_prompt_injections/test.csv          129
datasets/raw/zachz_prompt_injection_benchmark/train.csv  304
datasets/raw/chillies_ielts_task2/train.csv           484957
datasets/raw/chillies_ielts_task2/test.csv             24213
datasets/reports/v3/failure_analysis.jsonl               139
```

Registry gap:

- Raw deepset files exist, but `datasets/registry/sources.yaml` does not list `deepset/prompt-injections`.

## Claim Audit Findings

The following claims are not supported by the observed repository state:

- README claims frontend `/evidence`, but the frontend route does not exist.
- README claims Docker Compose, but no Docker/Compose artifacts exist.
- README and docs claim semantic embedding capability, while runtime falls back because `sentence_transformers` is unavailable.
- `docs/technical_report.md`, `docs/evaluation_report.md`, `docs/judge_qna.md`, `docs/demo_script_top1.md`, and frontend `judge-view` contain stale or unsupported metrics such as `0.90` Macro F1, `0.06` FPR, or `210ms` p95.
- Some docs answer or imply production readiness beyond the verified state.
- UI fallback values can display stronger metrics than the current evidence artifact.

Supported claims:

- Backend API routes exist and smoke-tested successfully.
- Backend unit tests pass when `PYTHONPATH=backend` is set.
- Frontend production build succeeds.
- Existing evidence artifacts report the handoff baseline metrics: 79% accuracy, 100% precision, 47% recall, 64% macro F1, 0% FPR, 21% under-block, 139 failures.

## Phase 0 Blockers

Phase 0 is not fully complete because:

- Frontend lint fails.
- Frontend `/evidence` route is missing despite README/docs claims.
- Docker claim is unsupported by repo artifacts.
- Existing tracked evidence artifacts still contain stale embedding state until safely regenerated or reviewed.
- Source/license registry is incomplete for raw datasets present in the repo.

## Safety Notes

- No Docker command was run.
- No volume, database, or cache cleanup was performed.
- No GAU IELTS file was modified.
- No dirty evidence/report file was overwritten.
- Python 3.13 test cache files generated during verification were removed after the run.

## Recommended Next Phase 0 Work

Before implementing product features:

- Make detector health evidence reflect actual runtime dependency/model state.
- Regenerate or review tracked evidence artifacts now that new runs reflect detector health honestly.
- Add or remove frontend `/evidence` claims.
- Remove unsupported Docker Compose claims or add verified Docker artifacts later in the deployment phase.
- Sync stale metrics in docs/UI from canonical evidence instead of hard-coded values.
