# ADR-009 Deterministic Demo Separation

Status: accepted

## Context

The project has a useful deterministic demo, but demo behavior is not measured production grader evidence.

## Decision

Keep deterministic demo surfaces clearly separate from measured evaluation and production adapter claims.

## Alternatives considered

- Present demo score recovery as real grader benchmark.
- Remove demo surfaces until real provider integration exists.

## Consequences

Judges can understand the idea without misleading metric claims.

## Later-phase implementation impact

Score Integrity track must identify adapter type and methodology in evidence.

