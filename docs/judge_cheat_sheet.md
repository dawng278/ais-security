# GradingGuard AI — Judge Cheat Sheet

> **Quick Reference Guide for Pitching, Answering Jury Questions & Staying on Strategy**

---

## Elevator Pitch Summaries

### 15-Second Version
> *"GradingGuard AI protects LLM-based IELTS grading from prompt injection and score manipulation by detecting malicious instructions, sanitizing them, securely grading the response, and verifying score integrity with reproducible evidence."*

### 30-Second Version
> *"Automated AI graders read student essay text directly as prompt context, making them vulnerable to instruction injection. In our core demo, a Vietnamese prompt payload inflates an authentic Band 5.5 essay to Band 8.5—a massive +3.0 bands exploit. GradingGuard AI detects the payload, strips the malicious span, and recovers score stability back to Band 5.5. The system also includes Attack Arena, Benchmark v3, Failure Analysis, Data Lineage, and Evidence Reports."*

---

## Core Proof Metrics

```text
Clean Essay Score:           Band 5.5
Injected Baseline (Vulnerable): Band 8.5
Protected Secure Score:        Band 5.5
Score Inflation Prevented:    +3.0 Bands
Defense Score Recovery:        +3.0 Bands
Score Stability Variance:       0.0
```

---

## Benchmark Accuracy & Under-Block Framing

### How to Explain 69% / 79% Accuracy
> *"Benchmark v3 is intentionally a robustness benchmark, not a polished leaderboard number. It includes broader prompt-injection edge cases, obfuscations, and diagnostic samples. We separate our evaluation into two tracks: On the **Core IELTS Score Integrity Track**, critical failure on score manipulation attacks is **0.0%**. On the **General Robustness Track**, failure analysis surfaces remaining edge cases to build an active engineering hardening roadmap."*

### How to Explain Under-Block Failure Cases
> *"Rather than hiding edge-case errors behind artificial 100% scores, Benchmark v3 uses transparent failure analysis to catalog every under-block into diagnostic categories (`critical_under_block`, `policy_under_block`, `threshold_near_miss`). In high-stakes AI evaluation, exposing failure diagnostics is essential for continuous hardening."*

---

## Defensive Language Guidelines (What to Say vs. What NOT to Say)

| DO NOT SAY | DO SAY | RATIONALE |
| :--- | :--- | :--- |
| ❌ *"Our system is fully production-ready."* | ✅ *"This is a competition-ready prototype with an explicit production hardening roadmap."* | Prevents overclaiming operational readiness while highlighting complete architecture. |
| ❌ *"GradingGuard AI prevents 100% of prompt injections."* | ✅ *"GradingGuard AI protects demonstrated core score manipulation attacks and transparently catalog broader robustness gaps."* | Maintains technical credibility and alignment with benchmark data. |
| ❌ *"Our benchmark accuracy is only 69%."* | ✅ *"Benchmark v3 is an evidence-driven robustness suite. Core IELTS score manipulation is protected with 0.0% critical failure."* | Focuses on core product value while framing general metrics as diagnostic research. |
| ❌ *"Keyword filtering catches prompt injections."* | ✅ *"We combine unicode normalization, multi-vector heuristic rules, semantic distance vectors, span sanitization, and XML boundary isolation."* | Emphasizes defense-in-depth engineering. |
