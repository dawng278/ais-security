# ADR-006 Audit Persistence Expectations

Status: accepted

## Context

Security decisions need evidence and accountability, especially when actions affect grading.

## Decision

Audit must be append-oriented, immutable after write, redacted by default, and corrected through new events.

## Alternatives considered

- Store only application logs.
- Allow direct edit/delete of audit records.

## Consequences

Persistent audit becomes a readiness blocker for pilot/enforce mode.

## Later-phase implementation impact

Phase 4 must add storage, redaction, integrity checks, and sensitive-content access audit.

