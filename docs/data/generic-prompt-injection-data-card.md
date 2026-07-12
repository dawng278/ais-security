# Generic Prompt Injection Data Card

Machine-readable manifest: `datasets/manifests/canonical_dataset_manifest.json`

## Composition

- Track: `generic_prompt_injection`
- Samples: 662
- Source: `hf_deepset_prompt_injections`
- License status: APPROVED
- Domain: `generic_llm_security`
- Language: English in current canonical records
- Labels: clean/benign/attack mapped from current repository artifacts

## Split

Deterministic group-hash split using:

- algorithm: `phase2_group_hash_v1`
- seed: `gradingguard_phase2_seed_20260713`
- group key: independence group/source record/normalized hash

## Duplicate and leakage handling

- Exact duplicate groups: see `datasets/manifests/deduplication_report.json`
- Near duplicate groups: see `datasets/manifests/near_duplicate_report.json`
- Holdout leakage: see `datasets/manifests/leakage_report.json`

Resolved benign template reuse is recorded and not silently deleted.

## Intended use

- Measure frozen detector behavior against current non-empty generic prompt-injection data.
- Preserve legacy baseline context without rewriting protected reports.

## Prohibited use

- Do not claim IELTS-domain robustness from this track alone.
- Do not tune detector thresholds in Phase 2.

## Limitations

- zachz rows are inventoried but excluded from canonical measured samples because the current processed artifact contains empty text for those rows.
- Embedding detector may be unavailable and must be reported in evidence.

