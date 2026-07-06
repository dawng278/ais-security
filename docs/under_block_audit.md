# GradingGuard AI — Under-Block Diagnostic Audit Report

## 1. Audit Executive Summary

- **Audit Target**: 139 remaining diagnostic failure cases from Benchmark v3 (662 total cases).
- **Post-P4 Accuracy**: **79.0%** (523 passed cases out of 662; improved from 69.0%).
- **critical_under_block Count**: **139** (reduced from 206 via P4 Heuristic & Policy Hardening).
- **Core IELTS Score Manipulation Failure Rate**: **0.0%** (0 critical score manipulation failures on core IELTS attacks).
- **False Positive Rate**: **6.0%** (benign cybersecurity essays preserved).

---

## 2. Failure Diagnostic Breakdown

All 139 remaining failures are transparently categorized in `datasets/reports/v3/failure_analysis.jsonl`:

| Diagnostic Category | Count | % of Failures | Security Impact Assessment |
| :--- | :---: | :---: | :--- |
| **`critical_under_block`** | 139 | 100.0% | Prompt injection payloads missed in pure CPU heuristic fallback mode. Zero impact on core IELTS score manipulation attacks. |
| **`policy_under_block`** | 0 | 0.0% | None. Policy engine correctly routes high-confidence signals to `secure_grade`. |
| **`threshold_near_miss`** | 0 | 0.0% | None. Risk thresholds tuned. |
| **`score_integrity_recovered`** | 0 | 0.0% | All core IELTS score manipulation attacks trigger secure grading. |

---

## 3. Evaluation Track Split

GradingGuard AI evaluates performance across two transparent tracks:

1. **Core IELTS Score Integrity Track**:
   - Primary product threat: IELTS band score manipulation.
   - Core demo: **5.5 → 8.5 → 5.5** (100% defense recovery, 0.0% critical score manipulation failure rate).
2. **General Prompt Injection Robustness Track**:
   - Secondary hardening track: Broad LLM prompt injection robustness.
   - Benchmark v3 accuracy: **79.0%** (139 under-blocks in CPU fallback mode; production ONNX embedding engine target: >92.0%).
