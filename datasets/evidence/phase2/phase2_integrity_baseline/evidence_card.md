# Phase 2 Evidence Card

Run ID: `phase2_integrity_baseline`

Status: generated and approved for Phase 2 integrity evidence.

## Dataset

- Canonical samples: 689
- Dataset hash: `a89eb6c09be417209af94f7026e319840195c4239202bec9639242b6a5511549`
- Split hash: `51e795858ff2d8460a4eeda9861407853a22bfbe6257dd9fd6bd3da983ef3fce`
- Metric definitions: `phase2_metrics_v1`

## Generic Prompt Injection

- Samples: 662
- Accuracy: 0.79
- Recall: 0.4715
- Failures: 139

## IELTS Domain Security

- Samples: 27
- Accuracy: 0.5556
- Recall: 0.2143
- Failures: 12

## Score Integrity

- Deterministic demo: DEMO_ONLY
- Measured track: NOT_MEASURED

## Operational Reliability

- Status: LOCAL_BENCHMARK
- Scenario count: 12
- p95 ms: 0.29
- Environment label: local benchmark; environment-specific; not production capacity

## Warnings

- No detector tuning was performed.
- Protected Phase 0/v3 reports were not modified.
- This evidence does not claim production capacity.
