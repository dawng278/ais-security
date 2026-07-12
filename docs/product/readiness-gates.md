# Readiness Gates

Status values: `READY`, `NOT_READY`, `BLOCKED`

## COMPETITION_READY

Current Phase 1 assessment: `READY` for architecture contract; full competition package remains later-phase work.

Requirements:

- Reproducible demo.
- Evidence card and report with honest metrics.
- Claim-drift guard.
- Benchmark methodology and limitations.
- Failure disclosure.
- Judge View.
- No production-readiness claim.

Gate:

- `READY` only when demo, evidence, tests, and claims are reproducible from the submitted repo.
- `NOT_READY` when non-critical evidence or packaging is missing.
- `BLOCKED` when core claims cannot be supported or protected evidence is unsafe.

## PILOT_READY

Current assessment: `NOT_READY`.

Additional requirements beyond competition:

- Shadow mode integration.
- Persistent append-oriented audit storage.
- Auth/RBAC.
- CORS and rate limiting.
- Redaction and retention controls.
- Manual review queue.
- Policy rollback.
- Observability.
- Backup and restore rehearsal.

Gate:

- `READY` only after a real integration can run in `shadow` or `warn` without modifying authoritative scores.
- `NOT_READY` when implementation exists but evidence is incomplete.
- `BLOCKED` when privacy, audit, or authorization controls are absent.

## PRODUCTION_READY

Current assessment: `BLOCKED` until pilot evidence and organizational approval exist.

Additional requirements beyond pilot:

- Pilot evidence.
- Load and capacity testing.
- Disaster recovery.
- Operational ownership.
- Security/privacy review.
- Enforce-mode gate.
- Validated real grader integration.

Gate:

- `READY` only when enforce mode has rollback, monitoring, review, and privacy controls.
- `NOT_READY` when remaining work is implementation-hardening.
- `BLOCKED` when legal/security review, data protection, or operational owner is missing.

