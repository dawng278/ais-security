# Phase 3 Before/After Evaluation

Prechange run: `datasets/evidence/phase3/phase3_prechange_baseline`

Final run:

`datasets/evidence/phase3/phase3_final_detection_engine`

## Result summary

Generic Prompt Injection:

- Accuracy: 0.79 -> 0.8369
- Recall: 0.4715 -> 0.5894
- Failure count: 139 -> 111
- Under-block count: 139 -> 111
- False-positive rate: 0.0 -> 0.0

IELTS Domain Security:

- Samples: 27
- Support: LOW_SUPPORT
- Accuracy: 0.5556 -> 0.8148
- Recall: 0.2143 -> 0.7143
- Failure count: 12 -> 6
- Under-block count: 11 -> 5
- False-positive rate: 0.0769 -> 0.0769

Comparison policy:

- identical sample IDs;
- frozen dataset hash;
- frozen split hash;
- no private-holdout content exported;
- IELTS track always marked LOW_SUPPORT;
- score integrity remains DETERMINISTIC_DEMO / NOT_MEASURED.

Metrics reported:

- accuracy;
- precision;
- recall;
- macro F1;
- false-positive rate;
- false-negative rate;
- under-block;
- over-block;
- changed predictions;
- latency p50/p95/p99.
