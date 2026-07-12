# ADR-003 Action Semantics

Status: accepted

## Context

Current backend actions are fewer than the product needs for competition and pilot semantics.

## Decision

Freeze actions as `allow`, `warn`, `sanitize`, `secure_grade`, `manual_review`, and `block`, while labeling current runtime support honestly.

## Alternatives considered

- Keep only current runtime actions.
- Use free-form action strings.

## Consequences

Later phases can implement missing actions without changing public semantics.

## Later-phase implementation impact

Policy engine, API schemas, review backend, and UI must use the frozen enum.

