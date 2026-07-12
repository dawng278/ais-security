# Grading Gateway API Contract

Status: Phase 1 contract; not wired as new runtime behavior.

Machine-readable schemas:

- `schemas/grading_request.schema.json`
- `schemas/grading_decision.schema.json`
- `schemas/grading_error.schema.json`

## Request contract

Required fields:

- `schema_version`: `grading_request.v1`.
- `request_id`: unique per submitted request.
- `correlation_id`: trace ID shared across logs, audit, frontend, and errors.
- `submission_id`: integration submission ID.
- `pseudonymous_user_id`: non-raw user identifier.
- `task_type`: `writing` or `speaking`.
- `candidate_content`: untrusted candidate text.
- `language`: BCP47-like language tag.
- `created_at`: ISO date-time.

Optional controlled fields:

- `grader_context`: rubric/prompt/module identifiers, never raw private prompts.
- `operating_mode_override`: accepted only from authorized internal callers in later phases.
- `policy_hints`: advisory and allowlisted; candidates must not control policy.
- `feature_flags`: boolean-only flags.
- `timeout_budget_ms`: bounded request budget.
- `metadata`: allowlisted client/environment/source hash.

## Decision contract

Required fields:

- `schema_version`: `grading_decision.v1`.
- `request_id`, `correlation_id`.
- `risk_score`, `severity`, `confidence`.
- `detected_techniques`.
- `detector_contributions`.
- `matched_evidence_refs`.
- `selected_action`: `allow`, `warn`, `sanitize`, `secure_grade`, `manual_review`, or `block`.
- `policy_id`, `policy_version`.
- `detector_health`.
- `latency_ms`.
- `sanitization_summary`.
- `review_state`.
- `grader_result_metadata`.
- `final_outcome`.
- `retryable`.
- `created_at`, `completed_at`.

Public responses must not expose regex internals, model cache paths, hidden thresholds, system prompts, credentials, raw sensitive evidence, private policy conditions, or stack traces.

## Error contract

| code | HTTP semantics | retryable | safe public message | internal reason code | audit required | correlation ID |
|---|---:|---|---|---|---|---|
| `INVALID_REQUEST` | 400 | no | Request is invalid. | `VALIDATION_FAILED` | yes | required |
| `UNSUPPORTED_SCHEMA_VERSION` | 400 | no | Request schema version is not supported. | `SCHEMA_VERSION_UNSUPPORTED` | yes | required |
| `REQUEST_TOO_LARGE` | 413 | no | Request is too large. | `CONTENT_LIMIT_EXCEEDED` | yes | required |
| `RATE_LIMITED` | 429 | yes | Too many requests. Please retry later. | `RATE_LIMIT_EXCEEDED` | yes | required |
| `DETECTOR_UNAVAILABLE` | 503 | yes | Security analysis is temporarily unavailable. | `DETECTOR_HEALTH_UNAVAILABLE` | yes | required |
| `POLICY_UNAVAILABLE` | 503 | yes | Security policy is temporarily unavailable. | `POLICY_STORE_UNAVAILABLE` | yes | required |
| `AUDIT_UNAVAILABLE` | 503 | yes | Audit logging is temporarily unavailable. | `AUDIT_STORE_UNAVAILABLE` | yes | required |
| `GRADER_TIMEOUT` | 504 | yes | Grading provider timed out. | `GRADER_TIMEOUT_BUDGET_EXCEEDED` | yes | required |
| `GRADER_INVALID_RESPONSE` | 502 | yes | Grading provider returned an invalid response. | `GRADER_SCHEMA_INVALID` | yes | required |
| `MANUAL_REVIEW_REQUIRED` | 202 | no | Submission requires manual review. | `REVIEW_QUEUE_CREATED` | yes | required |
| `REQUEST_BLOCKED` | 403 | no | Request was blocked by security policy. | `POLICY_BLOCKED_REQUEST` | yes | required |
| `UNAUTHORIZED` | 401 | no | Authentication is required. | `AUTH_REQUIRED` | yes | required |
| `FORBIDDEN` | 403 | no | You are not allowed to perform this action. | `RBAC_DENIED` | yes | required |
| `CONFLICT` | 409 | yes | Resource version conflict. Refresh and retry. | `OPTIMISTIC_LOCK_CONFLICT` | yes | required |
| `INTERNAL_ERROR` | 500 | yes | Unexpected internal error. | `UNEXPECTED_INTERNAL_ERROR` | yes | required |

No error path may expose stack traces.

