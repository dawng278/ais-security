# Detector Ensemble

Phase 3 ensemble version: `phase3_rules_v1`

Detector contributions are exposed as internal evidence:

- detector ID;
- detector version;
- runtime health;
- score contribution;
- confidence;
- technique IDs;
- evidence spans;
- latency;
- warnings;
- error reason.

Current detectors:

- `heuristic_rules`
- `obfuscation_detector`
- `semantic_embedding`

Unavailable detector output is not treated as a clean vote. Embedding remains truthful as unavailable/fallback unless dependency and model load succeed.

Aggregation is deterministic:

- heuristic score carries primary semantic intent;
- obfuscation score contributes bounded evidence;
- semantic score contributes only when available/fallback evidence exists;
- policy action is selected after risk aggregation, not inside a detector.

