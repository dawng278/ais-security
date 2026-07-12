# Benchmark Track Contracts

Status: Phase 1 contract

Canonical metric vocabulary:

- accuracy
- precision
- recall
- macro F1
- per-class F1
- FPR
- FNR
- under-block
- over-block
- attack success rate
- secure recovery rate
- score drift
- p50/p95/p99
- detector availability

## 1. Generic Prompt Injection (`generic_prompt_injection`)

- Purpose: measure baseline prompt-injection and hard-negative detection.
- Sample schema: id, source, text, label, attack_type, language, split, license_ref.
- Split rules: source-aware split; no near-duplicate leakage across train/tune/test.
- Metrics: accuracy, precision, recall, macro F1, FPR, FNR, under-block, over-block.
- Evidence artifacts: dataset hash, config hash, report JSON, failure analysis.
- Prohibited tuning: tuning on hidden/test split after seeing failures without recording lineage.
- Acceptance criteria: measured and reproducible; no artificial targets for competition optics.
- Limitations: does not prove IELTS grading score integrity by itself.

## 2. IELTS Domain Security (`ielts_domain_security`)

- Purpose: measure prompt attacks written as IELTS writing/speaking submissions.
- Sample schema: id, module, prompt_id, candidate_content, label, attack_type, language, split.
- Split rules: separate prompt families and task modules.
- Metrics: per-class F1, under-block, over-block, multilingual slices.
- Evidence artifacts: sanitized examples, redacted spans, prompt/rubric metadata.
- Prohibited tuning: hard-coding public Cambridge/IELTS prompt artifacts as detector rules without lineage.
- Acceptance criteria: domain examples and hard negatives represented separately.
- Limitations: not an official IELTS scoring validation.

## 3. Score Integrity (`score_integrity`)

- Purpose: measure whether secure grading reduces manipulation-driven score drift.
- Sample schema: clean_text, injected_text, clean_score, baseline_injected_score, secure_score, attack_type.
- Split rules: separate manipulation templates from evaluation samples.
- Metrics: attack success rate, secure recovery rate, score drift, invalid output rate.
- Evidence artifacts: grader adapter metadata, score delta report, verifier report.
- Prohibited tuning: using deterministic demo grader as measured real-grader evidence.
- Acceptance criteria: measured adapter and methodology are named.
- Limitations: depends on grader/provider behavior and rubric validation.

## 4. Operational Reliability (`operational_reliability`)

- Purpose: measure safe behavior under dependency failures and latency pressure.
- Sample schema: scenario_id, dependency_fault, operating_mode, expected_behavior, observed_behavior.
- Split rules: cover shadow/warn/enforce/degraded.
- Metrics: p50/p95/p99, detector availability, timeout rate, correct fail-mode behavior.
- Evidence artifacts: fault-injection logs, health snapshots, mode transition audit.
- Prohibited tuning: hiding failed dependency states behind successful demo flows.
- Acceptance criteria: failure-mode matrix is exercised.
- Limitations: local tests do not substitute for production load testing.

