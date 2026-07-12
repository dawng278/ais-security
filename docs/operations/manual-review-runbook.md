# Manual Review Runbook

State machine:

- `pending`
- `assigned`
- `in_review`
- `resolved_allow`
- `resolved_block`
- `escalated`
- `expired`

Phase 4 implements assignment and resolution with optimistic locking. A stale `expected_version` returns `CONFLICT`.

Reviewer notes are redacted before persistence. Raw sensitive input is hidden by default; restricted evidence access requires `sensitive:read` and writes a `sensitive_content_accessed` audit event.

