# GradingGuard AI — Benchmark v3 Evidence Card

> **Reproducible Security Evidence Record**  
> Generated: `2026-07-06T07:54:05.218114+00:00`

---

## 📌 Context Snapshot
- **Run ID**: `run_20260706_075405_f429a9`
- **Git Commit**: `2f2baa8`
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
- **Config SHA256**: `967615c90ee6cf78d0e87cf695726a5c8a572423146c9f2855d60951b3a09fac`

---

## 📊 Performance Metrics

### Overall Classification
| Metric | Value |
| :--- | :---: |
| **Accuracy** | `79.0%` |
| **Precision** | `100.0%` |
| **Recall** | `47.0%` |
| **Macro F1** | `64.0%` |
| **False Positive Rate** | `0.0%` |
| **Under-Block Rate** | `21.0%` |
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
