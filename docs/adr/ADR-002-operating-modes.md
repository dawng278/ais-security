# ADR-002 Operating Modes

Status: accepted

## Context

Security rollout needs observation, advisory, enforcement, and dependency-failure states.

## Decision

Freeze modes as `shadow`, `warn`, `enforce`, and `degraded`.

## Alternatives considered

- Single global on/off switch.
- Always fail-closed.
- Always fail-open with warning.

## Consequences

Mode-specific failure behavior is explicit, reducing silent unsafe fallback.

## Later-phase implementation impact

Mode transitions require RBAC, confirmation, audit, and rollback.

