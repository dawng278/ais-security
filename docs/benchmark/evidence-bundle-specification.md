# Evidence Bundle Specification

Approved-run pointer: `datasets/manifests/approved_evidence_run.json`

Run bundle path: `datasets/evidence/phase2/phase2_integrity_baseline`

## Required files

- `run_manifest.json`
- `metrics.json`
- `confusion_matrix.json`
- `failure_analysis.jsonl`
- `environment.json`
- `detector_health.json`
- `dataset_manifest.json`
- `score_integrity.json`
- `operational_reliability.json`
- `evidence_card.md`
- `checksum_manifest.json`

## Required metadata

- run ID;
- git commit;
- dirty worktree;
- environment;
- Python version;
- detector states;
- dataset hash;
- split hash;
- config hash;
- metric definitions version;
- warnings;
- limitations;
- protected report checksums.

Only approved runs may drive public measured claims. The pointer does not automatically publish results to README or UI.

