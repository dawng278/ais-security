# ADR-001 Gateway Placement

Status: accepted

## Context

GradingGuard must protect AI grading without becoming the IELTS platform itself.

## Decision

Place GradingGuard as a security gateway between GAU IELTS submission flow and the grader adapter.

## Alternatives considered

- Embed all logic inside GAU IELTS.
- Run only an offline benchmark tool.
- Place controls after grading only.

## Consequences

The gateway can enforce request/decision/audit contracts and be reused by other graders, but integration work is required.

## Later-phase implementation impact

Phase 4 must implement safe integration, auth/RBAC, audit persistence, and rollback before enforce mode.

