# ADR-004 Detector Ensemble Contract

Status: accepted

## Context

Detectors can fail independently, especially optional embedding dependencies.

## Decision

Every detector exposes standardized input/output, health, risk contribution, confidence, evidence, latency, and error reason.

## Alternatives considered

- Treat detector exceptions as backend errors.
- Hide optional detector health.

## Consequences

Embedding cannot be reported healthy when dependencies are missing; degraded states become visible.

## Later-phase implementation impact

Risk aggregation and health UI must consume detector state dimensions.

