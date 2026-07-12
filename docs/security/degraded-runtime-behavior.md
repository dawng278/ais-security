# Degraded Runtime Behavior

Phase 3 implements decision semantics compatible with Phase 1 modes.

Modes:

- `shadow`: calculate counterfactual action but authoritative action remains non-blocking.
- `warn`: attach warning and keep grading path available.
- `enforce`: apply deterministic policy action.
- `degraded`: use explicit fallback behavior, not a universal fail-open.

Current degraded examples:

- embedding unavailable: record unavailable health and continue with remaining detectors.
- detector unavailable with nontrivial risk: escalate to manual review in degraded policy.
- invalid policy: reject policy activation in later persistent implementation; static policy remains deterministic.
- sanitizer unsafe transformation: reject sanitization and preserve input.
- malformed grader output: raise validation error and map to safe error handling.

Persistent audit-write failure remains Phase 4 work, but Phase 3 decisions include audit-ready metadata.

