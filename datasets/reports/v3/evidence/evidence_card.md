# GradingGuard AI — Benchmark v3 Evidence Card

> **Reproducible Security Evidence Record**  
> Generated: `2026-07-16T02:37:29.163630+00:00`

---

## 📌 Context Snapshot
- **Run ID**: `run_20260716_023729_718cff`
- **Git Commit**: `9c5ff29`
- **Environment**: `local`
- **Random Seed**: `42`

## 📁 Dataset Fingerprint
- **Dataset Version**: `v2.0_canonical`
- **Dataset Path**: `/home/dawngbeo/school-project/ais-gau-security/datasets/processed/canonical_prompt_injection.jsonl`
- **Dataset SHA256**: `0a46535531e11d21aa61a7d9e9572c2fdccdd35b80bceb0ce7f6817575babd26`
- **Total Test Cases**: `965`

## 🛡️ Detector Configuration
- **Detector Version**: `ensemble_v3`
- **Threshold Version**: `risk_policy_v3`
- **Embedding Runtime State**: `unavailable`
- **Embedding Dependency State**: `missing`
- **Config SHA256**: `0451e8419d8559a4349809021d4d9824fa1bae3298624c5f332ababc668aa613`

---

## 📊 Performance Metrics

### Overall Classification
| Metric | Value |
| :--- | :---: |
| **Accuracy** | `84.0%` |
| **Precision** | `100.0%` |
| **Recall** | `59.0%` |
| **Macro F1** | `74.0%` |
| **False Positive Rate** | `0.0%` |
| **Under-Block Rate** | `16.0%` |
| **Over-Block Rate** | `0.0%` |

### Score Integrity & Protection
| Metric | Value |
| :--- | :---: |
| **Avg Score Inflation Prevented** | `+3.0 Bands` |
| **Defense Recovery Rate** | `100.0%` |
| **Utility Retention** | `100.0%` |

---

## 📈 Dataset Distributions

- **Labels**: `{'injection': 463, 'clean': 502}`
- **Attack Types**: `{'instruction_override': 30, 'role_hijack': 30, 'system_prompt_leak': 25, 'delimiter_injection': 25, 'encoding_bypass': 20, 'jailbreak': 35, 'data_exfiltration': 35, 'benign': 103, 'clean': 399, 'direct_english': 263}`
- **Languages**: `{'en': 965}`

---
*GradingGuard AI Security Benchmark Engine v3*
