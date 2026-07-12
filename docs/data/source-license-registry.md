# Source and License Registry

Authoritative machine-readable registry: `datasets/manifests/source_registry.json`

## Phase 2 source status

| source_id | source | license | approval_state | records used | notes |
|---|---|---|---|---:|---|
| `hf_deepset_prompt_injections` | deepset/prompt-injections | apache-2.0 | APPROVED | 662 | Primary non-empty generic canonical source. |
| `hf_zachz_prompt_injection_benchmark` | zachz/prompt-injection-benchmark | MIT | APPROVED | 303 inventory | Raw CSV present; processed JSONL rows are empty in current artifact, so excluded from measured canonical samples until parser repair. |
| `hf_chillies_ielts_task2` | chillies/IELTS-writing-task-2-evaluation | CC-BY-4.0 | APPROVED_WITH_RESTRICTIONS | 0 | Present locally; not used in Phase 2 canonical measured samples to avoid attribution/review mixing. |
| `internal_synthetic_ielts_security_v1` | internally authored IELTS security fixtures | INTERNAL-SYNTHETIC | INTERNAL_SYNTHETIC | 27 | Short non-copyrighted fixtures used for IELTS-domain security track. |
| `internal_operational_reliability_v1` | local operational reliability scenarios | INTERNAL-SYNTHETIC | INTERNAL_SYNTHETIC | 12 | Local benchmark only, not production capacity evidence. |
| `internal_score_integrity_demo_v1` | deterministic score demo | INTERNAL-SYNTHETIC | INTERNAL_SYNTHETIC | 1 | Demo-only; measured score track is NOT_MEASURED. |

UNKNOWN and REJECTED sources are not allowed in canonical measured artifacts.

## Review rule

License status is not inferred from source popularity. Every canonical source needs explicit license identifier, source hash, allowed use, and approval state in the JSON registry.

