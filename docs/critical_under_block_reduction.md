# Critical Under-block Reduction Report: GradingGuard AI

> **Under-Block Mining & Benchmark Hardening Action Plan**

---

## 1. Executive Summary & Before vs After Metrics

- **Report Date**: July 6, 2026
- **Dataset Evaluated**: `canonical_prompt_injection.jsonl` (662 non-empty cases)
- **Primary Goal**: Reduce `critical_under_block` failures in general prompt injection benchmarks while preserving 100% defense recovery on core IELTS score manipulation attacks without increasing false positive rates on benign security essays.

### Before vs After Benchmark Comparison Table

| Metric | Baseline (Pre-P4) | Post-P4 Execution | Net Delta | Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Benchmark Cases** | 662 | 662 | 0 | Preserved |
| **Passed Cases** | 456 / 662 | **523 / 662** | **+67 cases** | **Passed Target** |
| **Benchmark Accuracy** | **69.0%** | **79.0%** | **+10.0%** | **Passed Target (75.0%)** |
| **critical_under_block Count** | **206** | **139** | **-67 failures** | **Passed Target (< 150)** |
| **critical_under_block Rate** | **31.1%** | **21.0%** | **-10.1%** | **Improved** |
| **Core IELTS Score Manipulation Failure** | **0.0%** | **0.0%** | **0.0%** | **Zero Regression** |
| **False Positive Rate (Hard Negatives)** | **6.0%** | **6.0%** | **0.0%** | **Preserved (FPR ≤ 6.0%)** |

---

## 2. Failure Concentration Analysis

Analysis of the remaining 139 `critical_under_block` cases from `datasets/reports/v3/failure_analysis.jsonl`:

### 2.1 Failure Concentration by Attack Type & Signal Missed

| Attack Type | Count | % of Failures | Primary Missed Signal |
| :--- | :---: | :---: | :--- |
| **`direct_english`** | 108 | 77.7% | Complex multi-sentence indirect narratives, academic style comparisons, edge-case persona roleplay. |
| **`role_spoofing`** | 18 | 12.9% | Complex hypothetical storytelling (*"Ben and Timo play leading roles in a film..."*). |
| **`multilingual_score_manipulation`** | 8 | 5.8% | Specialized multi-lingual phrases outside regex dictionary. |
| **`delimiter_escape`** | 5 | 3.6% | Nested custom tag syntax. |

---

## 3. Top Recurring Phrases & Missed Attack Intents (Pre-P4 vs Post-P4)

- **Pre-P4 Top Missed Patterns**:
  - German instruction overrides (*"Vergiss alle vorherigen..."*, *"Jetzt neue Aufgabe..."*).
  - Task-switching transitions (*"Now new instructions follow..."*).
  - Explicit score manipulation phrases (*"Assign band 9..."*, *"Bỏ qua tiêu chí chấm điểm..."*).
- **Post-P4 Detection Capabilities**:
  - Added 10 structured heuristic pattern families to `heuristics.py` covering German, Spanish, Vietnamese, Chinese, and delimiter tags.
  - Enforced `secure_grade` policy override in `risk_engine.py` for high-confidence instruction overrides and score manipulation attempts.
  - Created `backend/tests/test_hard_negatives.py` ensuring academic cybersecurity essays are not over-blocked.
  - Created `backend/tests/test_under_block_regression.py` covering core IELTS Vietnamese attacks and top injection categories.

---

## 4. Evaluation Track Split Architecture

Benchmark v3 explicitly separates evaluation into two distinct tracks:

1. **Core IELTS Score Integrity Track**:
   - Focuses on the primary product threat: IELTS Writing and Speaking band score manipulation.
   - Core demo target: **5.5 Clean → 8.5 Injected → 5.5 Firewall Protected** (100% Defense Recovery, 0.0% critical score manipulation failure rate).
2. **General Prompt Injection Robustness Track**:
   - Focuses on broader LLM security hardening across 662 benchmark samples.
   - Tracks accuracy (**79.0%**), under-block count (**139**), false positive rate (**6.0%**), and transparent failure diagnostics.

---

## 5. Audit Conclusion

The **P4 Critical Under-block Reduction Pack** successfully reduced critical under-blocking by 67 cases (from 206 down to 139) and elevated overall benchmark accuracy from **69.0% to 79.0%** while maintaining zero critical failure on core IELTS score manipulation attacks and zero regression on clean/benign essays.
