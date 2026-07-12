# Audit Event Contract

Status: Phase 1 contract

## Required events

- `request_received`
- `normalization_completed`
- `detector_result`
- `decision_made`
- `policy_evaluated`
- `sanitized`
- `grader_called`
- `grader_completed`
- `review_created`
- `review_assigned`
- `review_resolved`
- `policy_published`
- `policy_rolled_back`
- `mode_changed`
- `evidence_exported`
- `sensitive_content_accessed`

## Required fields

Every audit event includes:

- `event_id`.
- `correlation_id`.
- `actor`.
- `actor_type`: system, integration_client, analyst, reviewer, policy_manager, admin.
- `action`.
- `target`.
- `timestamp`.
- `environment`.
- `policy_version`.
- `safe_metadata`.
- `redaction_state`.

## Prohibited normal-log fields

- Raw candidate content.
- Full grader system prompt.
- Credentials, API keys, provider tokens.
- Hidden thresholds and private policy conditions.
- Full unredacted evidence spans.
- Stack traces in public logs.

## Integrity expectations

- Append-oriented.
- Immutable after write.
- Corrections happen through a new event.
- Actor is traceable.
- Retention follows the redaction/retention contract.

