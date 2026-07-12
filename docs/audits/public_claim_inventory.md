# Public Claim Inventory

Status: Phase 0 current public-claim baseline.

Canonical measured source: `datasets/reports/v3/benchmark_v3_combined.json`

## Current Measured Metrics

| Claim | Value | Classification |
| --- | ---: | --- |
| Evaluated Benchmark v3 cases | 662 | MEASURED_CURRENT |
| Dataset fingerprint total | 965 | MEASURED_CURRENT |
| Accuracy | 79.0% | MEASURED_CURRENT |
| Precision | 100.0% | MEASURED_CURRENT |
| Recall | 47.0% | MEASURED_CURRENT |
| Macro F1 | 64.0% | MEASURED_CURRENT |
| False positive rate | 0.0% | MEASURED_CURRENT |
| Under-block rate | 21.0% | MEASURED_CURRENT |
| Diagnostic failure cases | 139 | MEASURED_CURRENT |

## Demo Claims

The 5.5 -> 8.5 -> 5.5 score recovery flow is classified as `DETERMINISTIC_DEMO`.
It may be used for judge storytelling only when separated from measured benchmark metrics.

## Runtime Claims

Embedding detector status is `unavailable` in the current runtime because `sentence-transformers`
is not installed. Public surfaces must not claim healthy embedding-derived performance.

Docker support is `ABSENT/UNVERIFIED` for Phase 0 because no Dockerfile or compose artifact exists.

Production readiness is `PLANNED`, not current. The accepted wording is competition prototype with a
production hardening path.

## Guard

`scripts/audit_public_claims.py` scans the configured public surfaces for stale metrics, unsupported
Docker claims, unsupported production-readiness wording, stale failure counts, and missing required
frontend routes. It exits non-zero on drift.
