# Phase 3 Detection and Decision Engine Report

Verdict: `PHASE_3_DETECTION_DECISION_ENGINE_DONE`

Date: 2026-07-13  
Repository: `/home/dawngbeo/school-project/ais-gau-security`  
Final evidence run: `phase3_final_detection_engine`

## Preflight and frozen hashes

- Starting accepted Phase 2 HEAD: `6c331e929c371a85acd99877a915fd0019ca27f6`
- Frozen canonical dataset hash: `a89eb6c09be417209af94f7026e319840195c4239202bec9639242b6a5511549`
- Frozen split hash: `51e795858ff2d8460a4eeda9861407853a22bfbe6257dd9fd6bd3da983ef3fce`
- Phase 2 evidence checks:
  - `datasets/evidence/phase2/phase2_integrity_baseline/run_manifest.json`: `e4d96d149ec26194301ee7cd15ab73d23667c0e97c6e244e08dd89943ca6d1cd`
  - `datasets/evidence/phase2/phase2_integrity_baseline/metrics.json`: `4483da1febbeeadf94ff004e1431c0984d76dedd06f9f23f79f95f39b74308dd`

Protected user-owned reports remained unchanged:

```text
863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003  datasets/reports/v3/benchmark_v3_combined.json
c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f  datasets/reports/v3/evidence/evidence_card.md
c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67  datasets/reports/v3/evidence/evidence_report.json
```

## Pre-registered objective

Objective from `docs/security/phase3_detector_improvement_plan.md`:

- reduce generic false negatives and under-blocking;
- keep generic false-positive rate at or below 0.08;
- retain IELTS LOW_SUPPORT label;
- do not use private-holdout content for tuning;
- do not modify dataset membership, labels, or split membership.

## Detector and decision changes

Preprocessing:

- Unicode NFKC, zero-width removal, bidirectional-control removal, control-character handling.
- URL-encoded evidence detection.
- Bounded Base64 text decoding with decoded-size limits.

Rule detector:

- Added general Phase 3 rule families for additional/new instructions, response hijack, prompt extraction, cross-user data requests, context/document bypass, persona reassignment, policy bypass, IELTS examiner impersonation, rubric override, Band 9 manipulation, Vietnamese/mixed-language attacks, German override variants, and coercive instruction pressure.
- Added benign context dampening for quoted/academic/security discussion hard negatives.

Policy/ensemble:

- Added detector contribution fields to analyzer response.
- Added deterministic static policy engine with `shadow`, `warn`, `enforce`, and `degraded` semantics.
- Covered all six Phase 1 actions in schema/policy: `allow`, `warn`, `sanitize`, `secure_grade`, `manual_review`, `block`.

Sanitization:

- Span-based replacement, overlap merge, max transformation count, idempotency, and rejection of transformations that would remove most content.

Protected grader:

- Added explicit protected grader request boundary and score/rubric-field validation around the deterministic mock grader.
- Score integrity remains `DETERMINISTIC_DEMO`; measured track remains `NOT_MEASURED`.

Embedding:

- No large model was downloaded.
- Runtime remains truthful: embedding unavailable when `sentence-transformers` is unavailable.
- Missing embedding does not count as a clean vote.

## Before/after metrics

Generic Prompt Injection:

| metric | before | after | delta |
|---|---:|---:|---:|
| samples | 662 | 662 | 0 |
| accuracy | 0.79 | 0.8369 | +0.0469 |
| precision | 1.0 | 1.0 | 0 |
| recall | 0.4715 | 0.5894 | +0.1179 |
| macro F1 | 0.7462 | 0.8112 | +0.065 |
| false-positive rate | 0.0 | 0.0 | 0 |
| false-negative rate | 0.5285 | 0.4106 | -0.1179 |
| failure count | 139 | 111 | -28 |
| under-block count | 139 | 111 | -28 |
| over-block count | 0 | 0 | 0 |

IELTS Domain Security, LOW_SUPPORT:

| metric | before | after | delta |
|---|---:|---:|---:|
| samples | 27 | 27 | 0 |
| accuracy | 0.5556 | 0.8148 | +0.2592 |
| precision | 0.75 | 0.9091 | +0.1591 |
| recall | 0.2143 | 0.7143 | +0.5 |
| macro F1 | 0.5 | 0.8138 | +0.3138 |
| false-positive rate | 0.0769 | 0.0769 | 0 |
| false-negative rate | 0.7857 | 0.2857 | -0.5 |
| failure count | 12 | 6 | -6 |
| under-block count | 11 | 5 | -6 |
| over-block count | 1 | 0 | -1 |

Changed prediction summary:

- corrected failures: 34
- changed failures: 5
- action changed without failure: 3
- total changed predictions: 42

Statistical comparison:

- paired sample comparison by identical sample IDs;
- absolute generic failure reduction: 28;
- generic false-positive increase: 0;
- IELTS result is reported only with LOW_SUPPORT warning.

Latency:

| run | p50 ms | p95 ms | p99 ms | max ms |
|---|---:|---:|---:|---:|
| prechange | 0.038 | 0.086 | 0.148 | 0.788 |
| final | 0.096 | 0.305 | 0.528 | 3.133 |

Latency increased because Phase 3 performs richer normalization and rule matching; this is local benchmark data, not production capacity.

## Overfitting guard

Automated guard in `backend/tests/test_phase3_detection_engine.py` verifies:

- no canonical sample IDs in detector source;
- no long exact canonical sample content embedded in detector rules.

Private-holdout content is not exported in failure reports.

## Evidence

Final approved bundle:

- `datasets/evidence/phase3/phase3_final_detection_engine`
- run manifest checksum: `f68e4208016df63e0e558f9c4f0ef2e371d9c46b98d891a47fc3a8f027cc770d`
- metrics checksum: `2484ac00a1114d8aa735cbb7b6613ee41fa41dbc9c41f2ba67f96c0cbdab35df`

Required files are present, including manifest, metrics, comparison, changed predictions, failure analysis, detector health, contribution summary, policy/action summary, calibration, latency, environment, dataset/config manifests, checksums, evidence card, and limitations.

## Verification

- Backend tests: 69 passed.
- Phase 1 contract tests: included in backend suite.
- Phase 2 data-integrity tests: included in backend suite.
- Dataset integrity gate: PASS.
- Claim-drift guard: PASS.
- Frontend lint: PASS.
- Frontend typecheck: PASS.
- Frontend build: PASS.
- `git diff --check`: PASS.
- Protected checksum verification: PASS.
- Phase 2 evidence checksum verification: PASS.
- GAU IELTS HEAD unchanged: `f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7`.

## Limitations and warnings

- IELTS-domain track remains LOW_SUPPORT.
- Embedding remains unavailable unless optional dependency/model are actually present.
- Score integrity remains `DETERMINISTIC_DEMO`; measured score integrity remains `NOT_MEASURED`.
- Local latency is not production capacity.
- Persistent audit, auth/RBAC, policy storage, and manual-review persistence remain Phase 4+ work.

Unresolved critical detector/policy decisions: 0.

