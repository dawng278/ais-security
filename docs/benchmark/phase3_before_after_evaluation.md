# Phase 3 Before/After Evaluation

Prechange run: `datasets/evidence/phase3/phase3_prechange_baseline`

Final run will be generated after detector freeze into:

`datasets/evidence/phase3/phase3_final_detection_engine`

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

