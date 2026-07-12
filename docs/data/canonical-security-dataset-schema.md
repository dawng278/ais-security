# Canonical Security Dataset Schema

Schema file: `schemas/canonical_security_sample.schema.json`  
Schema version: `canonical_security_sample.v1`

The schema separates:

- gold `security_label`;
- detector prediction;
- expected policy/action range.

This prevents benchmark code from turning current detector behavior into ground truth.

## Required identity fields

- `sample_id`: deterministic `ggs_<16 hex>` derived from schema version, source ID, source record ID, and normalized hash.
- `content_hash`: SHA-256 over raw content.
- `normalized_hash`: SHA-256 over deterministic normalized text.
- `independence_group`: group-aware split key for source lineage, pairs, and variants.

IDs never depend on UUIDs, timestamps, file order, or local paths.

## Required provenance fields

- source path;
- generation method;
- generator type;
- template version;
- human review status.

Synthetic samples record human-authored fixture provenance. No LLM-generated label is treated as sole authority.

## Split values

`train`, `validation`, `public_test`, `private_holdout`, `development`, `measured_holdout`, `failure_injection`.

## Benchmark tracks

`generic_prompt_injection`, `ielts_domain_security`, `score_integrity`, `operational_reliability`.

