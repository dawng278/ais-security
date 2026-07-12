# Phase 2 Dataset, Benchmark and Evidence Integrity Report

Verdict: `PHASE_2_DATASET_BENCHMARK_EVIDENCE_DONE`

Date: 2026-07-13  
Repository: `/home/dawngbeo/school-project/ais-gau-security`  
Phase 2 evidence run: `phase2_integrity_baseline`

## Preflight

- Branch: `main`.
- Starting HEAD: `2e9a285b88f5c84f28180589a79afbe6f73d0c9c`.
- Existing dirty files classified as `USER_EXISTING_WORK`:
  - `datasets/reports/v3/benchmark_v3_combined.json`
  - `datasets/reports/v3/evidence/evidence_card.md`
  - `datasets/reports/v3/evidence/evidence_report.json`
- No detector rules, weights, thresholds, or action routing were changed.
- No Docker, auth/RBAC, persistent audit DB, frontend redesign, paid API, large model download, or GAU IELTS repo change was performed.

## Protected report checksums

Before and after Phase 2:

```text
863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003  datasets/reports/v3/benchmark_v3_combined.json
c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f  datasets/reports/v3/evidence/evidence_card.md
c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67  datasets/reports/v3/evidence/evidence_report.json
```

Result: unchanged.

## Dataset inventory and source/license result

Authoritative registry: `datasets/manifests/source_registry.json`

Canonical source states:

- APPROVED: `hf_deepset_prompt_injections`, `hf_zachz_prompt_injection_benchmark`.
- APPROVED_WITH_RESTRICTIONS: `hf_chillies_ielts_task2`.
- INTERNAL_SYNTHETIC: `internal_synthetic_ielts_security_v1`, `internal_operational_reliability_v1`, `internal_score_integrity_demo_v1`.

No UNKNOWN or REJECTED source is included in canonical measured artifacts.

## Canonical schema

- Schema: `schemas/canonical_security_sample.schema.json`
- Version: `canonical_security_sample.v1`
- Deterministic IDs: `ggs_<16 hex>`
- Raw and normalized hashes are stored separately.
- Gold labels, detector predictions, and expected action ranges are separate concepts.

## Sample totals and composition

- Total canonical samples: 689
- Generic Prompt Injection: 662
- IELTS Domain Security: 27

Languages:

- en: 686
- vi: 1
- vi-en: 2

Domains:

- generic_llm_security: 662
- ielts_writing_task_2: 16
- ielts_reading: 5
- ielts_speaking: 4
- ielts_writing_task_1: 2

Attack-family coverage:

- direct_prompt_injection: 264
- none: 412
- indirect_prompt_injection: 2
- multilingual_attack: 2
- data_exfiltration, delimiter_abuse, encoding_attack, long_context_attack, policy_manipulation, role_spoofing, score_manipulation, system_prompt_extraction, unicode_obfuscation: 1 each

Hard-negative coverage is documented in `docs/data/ielts-domain-security-data-card.md`.

## Duplicate, near-duplicate and leakage result

- Exact duplicate groups: 0
- Unresolved measured duplicate count: 0
- Near-duplicate groups: 8
- Near-duplicate method: deterministic token Jaccard, threshold 0.92, no embeddings.
- Resolved near-duplicate holdout findings: 5
- Unresolved holdout leakage: 0

Near duplicates are recorded, not silently deleted.

## Split result

- Algorithm: `phase2_group_hash_v1`
- Seed: `gradingguard_phase2_seed_20260713`
- Split hash: `51e795858ff2d8460a4eeda9861407853a22bfbe6257dd9fd6bd3da983ef3fce`
- Counts:
  - train: 493
  - public_test: 89
  - private_holdout: 107

Canonical build was checked twice and produced identical dataset and split hashes.

## Benchmark results

Legacy safe rerun:

- Output path: `/tmp/ais_phase2_legacy_v3`
- Total cases: 662
- Accuracy: 0.79
- Failures: 139
- Protected reports: unchanged

Generic canonical baseline:

- Samples: 662
- Accuracy: 0.79
- Recall: 0.4715
- Failure cases: 139

IELTS-domain baseline:

- Samples: 27
- Accuracy: 0.5556
- Recall: 0.2143
- LOW_SUPPORT warnings apply to small slices.

Score Integrity:

- Deterministic demo: `DEMO_ONLY`
- Measured score-integrity: `NOT_MEASURED`
- No hard-coded demo result is accepted as measured evidence.

Operational Reliability:

- Status: `LOCAL_BENCHMARK`
- Scenarios: 12
- p95: 0.29 ms in this local run
- Environment label: local benchmark, environment-specific, not production capacity.

## Metric definitions and failure taxonomy

- Metric definitions: `phase2_metrics_v1`
- Failure taxonomy: `phase2_failure_taxonomy_v1`
- Low-support threshold: 20 samples per slice.

## Evidence bundle and approved-run mechanism

Approved-run pointer: `datasets/manifests/approved_evidence_run.json`

Evidence bundle:

- `datasets/evidence/phase2/phase2_integrity_baseline`
- Bundle hash: `232e6fcecf974a7782bc3e78a91a8fea94b104590efe2d97ed27ae2d41f8f2f1`
- Status: approved for Phase 2 integrity evidence only.

The approved-run pointer does not automatically publish results to README/UI.

## Lineage result

Lineage fields in canonical samples and manifests include source, revision, license, raw hash, normalized hash, dedup result, split, benchmark tracks, annotation status, approval state, and run usage. Counts are generated from actual canonical records.

## Verification

Commands run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend:. python -m pytest backend/tests -q
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python scripts/audit_public_claims.py
python scripts/audit_dataset_integrity.py
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/eslint
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/tsc --noEmit
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/next build
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend GRADINGGUARD_REPORTS_V3_DIR=/tmp/ais_phase2_legacy_v3 python -m app.benchmark.runner_v3
git diff --check
```

Results:

- Backend tests: 50 passed.
- Dataset integrity gate: PASS.
- Claim-drift guard: PASS.
- Frontend lint: PASS.
- Frontend typecheck: PASS.
- Frontend build: PASS.
- Legacy safe rerun: 662 cases, 79.0% accuracy, 139 failures.
- Protected report checksum comparison: PASS.
- GAU IELTS HEAD unchanged: `f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7`.
- GAU IELTS dirty status unchanged from preflight.

## Blockers and warnings

Blockers: none for Phase 2.

Warnings:

- IELTS-domain track is intentionally small and LOW_SUPPORT.
- Measured score-integrity is NOT_MEASURED until an approved evaluator/grader adapter exists.
- Operational reliability is local and not production capacity.
- Embedding detector remains unavailable when `sentence-transformers` is missing.
- Phase 3 detector/policy tuning is not started by this report.

Unresolved critical data/license decisions: 0.

