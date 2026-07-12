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
- Existing pages at initial audit: `/`, `/dashboard`, `/judge-view`, `/playground`, `/attack-arena`, `/benchmark`, `/data-lineage`
- The missing frontend `/evidence` route was added after the initial audit.

Data and evidence:

- Canonical processed dataset: `datasets/processed/canonical_prompt_injection.jsonl`
- Existing v3 reports: `datasets/reports/v3/*`
- Existing evidence card/report: `datasets/reports/v3/evidence/*`
- Source registry: `datasets/registry/sources.yaml`
- License registry: `datasets/registry/licenses.md`

Deployment:

- No `Dockerfile`, `docker-compose.yml`, or `.dockerignore` was found in the repo root or project tree at audit time.
- README initially claimed Docker Compose support; this was downgraded to an explicit unverified Docker status after the audit.

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
/evidence
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
- This was fixed after the initial audit by adding `deepset/prompt-injections` with Apache-2.0 license metadata verified from the Hugging Face dataset page on 2026-07-13.

## Claim Audit Final State

Public claim inventory:

- Human-readable: `docs/audits/public_claim_inventory.md`
- Machine-readable: `docs/audits/public_claim_inventory.json`

Automated guard:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python scripts/audit_public_claims.py
```

Result:

```text
Public claim audit: PASS
Canonical metric source: datasets/reports/v3/benchmark_v3_combined.json
Findings: 0
```

Resolved public claim drift:

- `/evidence` is now a real frontend route and appears in the Next build route table.
- Docker Compose is no longer claimed as verified.
- Deterministic 5.5 -> 8.5 -> 5.5 score recovery is labelled as a demo, not a measured LLM benchmark.
- Stale public values such as Macro F1 0.90, FPR 0.06, p95 210 ms, and 3,000 attacks were removed or relabelled on configured public surfaces.
- Current public metric claims are synchronized to 79.0% accuracy, 100% precision, 47% recall, 64% Macro F1, 0.0% FPR, 21.0% under-block, and 139 diagnostic failures.
- Embedding runtime is represented as optional/unavailable instead of healthy.
- Production readiness wording was changed to competition prototype / hardening path language.

## Capability Classification

| Capability | Classification | Evidence |
| --- | --- | --- |
| FastAPI health and API routers | IMPLEMENTED_AND_VERIFIED | API smoke returned 200 |
| Firewall analyze | IMPLEMENTED_AND_VERIFIED | `POST /api/firewall/analyze` smoke returned 200 |
| Grade compare | DETERMINISTIC_DEMO | mock grader route smoke returned 200 |
| Benchmark v3 runner | IMPLEMENTED_AND_VERIFIED | isolated rerun in `/tmp/ais_gau_security_phase0_final_benchmark` |
| Evidence generator | IMPLEMENTED_AND_VERIFIED | isolated evidence records embedding unavailable |
| Frontend `/evidence` | IMPLEMENTED_AND_VERIFIED | Next build lists dynamic `/evidence` route |
| Dashboard telemetry | MOCK/PARTIAL | API-backed or seeded fallback, labelled in UI |
| Attack Arena | DETERMINISTIC_DEMO/PARTIAL | API route exists; seeded scenario behavior remains demo-oriented |
| Data lineage | PARTIAL | API route exists; broader source/license due diligence remains future work |
| Docker deployment | NOT_IMPLEMENTED | no Dockerfile or compose artifacts found |
| Auth/RBAC | NOT_IMPLEMENTED | no auth boundary verified in Phase 0 |
| Persistent audit DB | NOT_IMPLEMENTED | current reports are file artifacts, not operational audit storage |
| Manual review backend | NOT_IMPLEMENTED | action exists, persistent workflow not implemented |
| Policy management UI/backend | NOT_IMPLEMENTED | no verified policy versioning workflow |

## Route And API Truth Table

| Frontend route | File | Build result | Backend/API dependency | Data status |
| --- | --- | --- | --- | --- |
| `/` | `frontend/src/app/page.tsx` | PASS | none critical | static |
| `/dashboard` | `frontend/src/app/dashboard/page.tsx` | PASS | `/api/dashboard/stats`, `/api/dashboard/events` | API or seeded fallback |
| `/judge-view` | `frontend/src/app/judge-view/page.tsx` | PASS | evidence, benchmark, lineage APIs | measured + deterministic demo |
| `/attack-arena` | `frontend/src/app/attack-arena/page.tsx` | PASS | `/api/arena/profiles`, `/api/arena/run` | deterministic demo/API |
| `/playground` | `frontend/src/app/playground/page.tsx` | PASS | firewall/grade/redteam APIs | API demo |
| `/benchmark` | `frontend/src/app/benchmark/page.tsx` | PASS | benchmark/evidence APIs | measured or unavailable |
| `/data-lineage` | `frontend/src/app/data-lineage/page.tsx` | PASS | `/api/lineage/report` | partial lineage |
| `/evidence` | `frontend/src/app/evidence/page.tsx` | PASS | `/api/evidence/latest` | measured or unavailable |

API smoke result:

```text
GET  /health                              200
GET  /api/dashboard/stats                 200
GET  /api/dashboard/events                200
GET  /api/arena/profiles                  200
GET  /api/benchmark/v3/report             200
GET  /api/benchmark/v3/failure-analysis   200
GET  /api/lineage/report                  200
GET  /api/evidence/latest                 200
POST /api/firewall/analyze                200
POST /api/grade/compare                   200
```

## Final Verification

```text
Backend tests: 33 passed
Frontend lint: PASS
Frontend typecheck: PASS
Frontend build: PASS
Claim drift guard: PASS
Safe Benchmark v3 rerun: 662 cases, 79.0% accuracy, 139 failures
Embedding in safe rerun: enable_embedding_detector=false, runtime_state=unavailable
Protected report checksums before/after: unchanged
GAU IELTS HEAD: f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7
GAU IELTS status: unchanged from preflight dirty state
```

Protected report checksums:

```text
863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003  datasets/reports/v3/benchmark_v3_combined.json
c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f  datasets/reports/v3/evidence/evidence_card.md
c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67  datasets/reports/v3/evidence/evidence_report.json
```

## Phase 0 Verdict

```text
PHASE_0_REPOSITORY_TRUTH_AUDIT_DONE
```

Phase 1 is authorized from the repository-truth perspective only. Phase 1 must still avoid protected dirty reports and must not implement deployment, auth, persistence, or frontend management overhaul unless those are explicitly in the next phase scope.

## Safety Notes

- No Docker command was run.
- No volume, database, or cache cleanup was performed.
- No GAU IELTS file was modified.
- No dirty evidence/report file was overwritten.
- Python 3.13 test cache files generated during verification were removed after the run.

## Recommended Next Phase 0 Work

None. Phase 0 acceptance gates are complete.

Recommended Phase 1 prerequisites:

- Regenerate or review tracked evidence artifacts now that new runs reflect detector health honestly.
- Add verified Docker artifacts later in the deployment phase before restoring any Docker support claim.
- Start architecture/product contract work from the truth inventory instead of from older overclaiming docs.
