# Safe Explanations

Phase 3 uses stable public reason codes instead of exposing detector internals.

Allowed public fields:

- severity;
- selected action;
- stable reason code;
- correlation ID when available;
- generic technique label.

Internal-only fields:

- detector contributions;
- matched technique IDs;
- normalization transformations;
- policy rule ID;
- risk-band mapping;
- selected action reason.

Never expose publicly:

- full regex;
- hidden thresholds;
- system prompts;
- model paths/cache paths;
- internal policy expressions;
- raw secret-like content;
- exploit-development detail.

