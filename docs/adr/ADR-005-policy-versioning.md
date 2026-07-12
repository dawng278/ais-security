# ADR-005 Policy Versioning

Status: accepted

## Context

Enforce mode is unsafe without deterministic, auditable policy versions and rollback.

## Decision

Policies move through draft, validated, published, active/monitored, superseded or rolled_back, and archived states.

## Alternatives considered

- Hard-code thresholds only.
- Permit arbitrary code policies.

## Consequences

Policy changes are slower but auditable and reversible.

## Later-phase implementation impact

Phase 3/4 must build validation, publish, rollback, conflict resolution, and audit events.

