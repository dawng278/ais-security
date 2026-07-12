# ADR-008 Benchmark Track Separation

Status: accepted

## Context

Generic injection accuracy is not the same as IELTS-domain safety, score integrity, or reliability.

## Decision

Separate tracks: `generic_prompt_injection`, `ielts_domain_security`, `score_integrity`, and `operational_reliability`.

## Alternatives considered

- One blended benchmark score.
- Competition-only curated demo cases.

## Consequences

Claims become more honest and failures more actionable.

## Later-phase implementation impact

Phase 2 must preserve track separation, sample schemas, metrics, and evidence artifacts.

