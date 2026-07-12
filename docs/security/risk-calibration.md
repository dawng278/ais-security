# Risk Calibration

Phase 3 calibration version: `phase3_static_weighted_v1`

The score is a bounded risk indicator, not a calibrated probability.

Inputs:

- heuristic score;
- obfuscation score;
- semantic score;
- matched high-impact categories.

Risk bands:

- low: `< 0.25`
- medium: `0.25–0.49`
- high: `0.50–0.89`
- critical: `>= 0.90`

Policy can escalate high-impact categories such as prompt extraction, policy bypass, data exfiltration, delimiter escape, role spoofing, and score manipulation.

Calibration did not use private-holdout content. Final before/after comparison is paired by sample ID.

