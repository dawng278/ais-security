# ADR-007 Manual Review Workflow

Status: accepted

## Context

High-impact or ambiguous submissions should not be silently allowed or blocked.

## Decision

Manual review uses states `pending`, `assigned`, `in_review`, `resolved_allow`, `resolved_block`, `escalated`, and `expired`.

## Alternatives considered

- Simple boolean reviewed flag.
- Email/offline-only review.

## Consequences

Review is auditable and conflict-safe but requires backend and UI implementation later.

## Later-phase implementation impact

Review queue needs RBAC, optimistic locking, SLA, notes, and audit trail.

