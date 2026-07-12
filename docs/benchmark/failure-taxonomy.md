# Failure Taxonomy

Machine-readable taxonomy: `datasets/manifests/failure_taxonomy.json`

Version: `phase2_failure_taxonomy_v1`

Categories:

- false_negative
- false_positive
- under_block
- over_block
- span_miss
- normalization_failure
- semantic_miss
- language_gap
- long_context_miss
- obfuscation_miss
- detector_unavailable
- policy_routing_error
- grader_error
- benchmark_data_error
- ambiguous_label
- source_conflict

Public failure reports must not store full sensitive input by default. Required fields include sample ID, track, split, true label, predicted label, risk score, selected action, expected action range, detector contributions, failure category, and run ID.

