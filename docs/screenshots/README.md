# GradingGuard AI — Screenshot Package Guide

This directory contains instructions for taking and naming backup screenshots of GradingGuard AI for competition submission, presentation slides, and video editing.

> **Note**: Screenshots serve as backup visual assets for judging panels and slide decks. They should complement—not replace—the live interactive application unless the live network environment is unavailable.

---

## Required Screenshot List & Naming Conventions

| Filename | Page / Target UI | Required View / Element | Key Purpose |
| :--- | :--- | :--- | :--- |
| `01_judge_view.png` | `/judge-view` | Hero section, 5.5 → 8.5 → 5.5 core demo banner, Defense Recovery (+3.0) | Executive 60-second summary |
| `02_playground_clean_score.png` | `/playground` | Clean essay submission showing Band 5.5, `ALLOW` status, low risk | Baseline utility preservation |
| `03_playground_attack_baseline.png` | `/attack-baseline` | Injected Vietnamese attack with firewall **OFF** showing Band 8.5 | Exploit demonstration (+3.0 inflation) |
| `04_playground_secure_recovery.png` | `/playground` | Firewall **ON**, removed malicious span highlighted, secure Band 5.5 | Defense recovery (+3.0 recovery) |
| `05_attack_arena.png` | `/attack-arena` | Adaptive/multilingual attacker profiles, attempt replay table, score inflation prevented | Adversarial red-team resilience |
| `06_benchmark_overview.png` | `/benchmark` | Overview metrics cards (Accuracy, F1, Defense Recovery) | High-level evaluation metrics |
| `07_benchmark_failure_analysis.png` | `/benchmark` | Failure Analysis tab, 4 diagnostic categories, next engineering fix cards | Transparent error classification |
| `08_data_lineage.png` | `/data-lineage` | Dataset SHA256, 7 registered sources, 8-stage transformation pipeline diagram | Provenance & split transparency |
| `09_evidence_report.png` | `/evidence` or `/judge-view` | Evidence Card modal/section with `dataset_sha256`, `config_sha256`, `git_commit` | Cryptographic auditability |

---

## Capture Guidelines

1. **Resolution**: Set display resolution to 1920x1080 (1080p) or 2560x1440 (1440p) at 100% DPI scale.
2. **Browser Frame**: Use Chrome/Brave in clean window mode or full-bleed desktop view (dark mode theme active).
3. **Data State**: Ensure backend server is active and populated with verified Benchmark v3 execution output (`datasets/reports/v3`).
