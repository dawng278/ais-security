# ADR-010 GAU IELTS UI Alignment

Status: accepted

## Context

The security console should feel compatible with GAU IELTS without copying source or mutating the reference repo.

## Decision

Use a local GradingGuard UI layer inspired by GAU IELTS design tokens, cards, buttons, state components, and responsive patterns.

## Alternatives considered

- Copy GAU IELTS components directly.
- Keep the current dark-only security UI unchanged.

## Consequences

The console can align visually while preserving repository boundaries and security-specific UX.

## Later-phase implementation impact

Frontend phase should build tokenized severity/mode/evidence components and label measured/demo/planned states.

