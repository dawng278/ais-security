# Action Semantics

Supported actions: `allow`, `warn`, `sanitize`, `secure_grade`, `manual_review`, `block`.

Current runtime note: `allow`, `warn`, `secure_grade`, and `manual_review` exist in current backend schemas. `sanitize` and `block` are contracted Phase 1 semantics for later runtime implementation.

## `allow`

- Trigger conditions: low risk, sufficient detector health, no policy match requiring stronger action.
- Required evidence: risk score, detector health, policy version, correlation ID.
- Effect on input: no content transformation.
- Effect on grader: normal protected path may proceed.
- Effect on final response: grading proceeds without user-visible security warning.
- Audit events: `request_received`, `detector_result`, `policy_evaluated`, `decision_made`.
- Retry behavior: retry only for transient dependencies before final decision.
- User-visible response: normal grading result.
- Analyst-visible response: low-risk decision remains searchable.
- Failure behavior: if core audit/policy unavailable in enforce, follow failure matrix.
- Prohibited behavior: `allow` does not mean “no risk” and must not erase audit metadata.

## `warn`

- Trigger conditions: medium risk, degraded confidence, or policy chooses advisory handling.
- Required evidence: risk reasons, warning reason code, detector health.
- Effect on input: no mandatory transformation.
- Effect on grader: grading continues.
- Effect on final response: warning may be attached depending on integration policy.
- Audit events: standard decision events plus warning metadata.
- Retry behavior: retry transient detector/grader failures within timeout budget.
- User-visible response: safe public warning, not detector internals.
- Analyst-visible response: warning reason and redacted evidence.
- Failure behavior: continue-with-warning where matrix permits.
- Prohibited behavior: no silent score modification.

## `sanitize`

- Trigger conditions: policy determines risky span can be safely removed or neutralized.
- Required evidence: structured transformation evidence, removed span references, original hash.
- Effect on input: produces sanitized candidate content.
- Effect on grader: grader receives sanitized content only.
- Effect on final response: may say content was processed under security controls.
- Audit events: standard decision events plus `sanitized`.
- Retry behavior: no blind retry that changes transformation semantics.
- User-visible response: stable reason code, no regex internals.
- Analyst-visible response: redacted original/sanitized diff when permitted.
- Failure behavior: if sanitizer cannot produce evidence, escalate to `manual_review`.
- Prohibited behavior: must never silently delete arbitrary essay content; original content may be retained only in protected audit storage when policy permits.

## `secure_grade`

- Trigger conditions: high risk, score-manipulation signal, or policy requires protected grading.
- Required evidence: detector contributions, policy decision, grader adapter metadata, validation result.
- Effect on input: may use normalized/sanitized content depending on policy.
- Effect on grader: must use a grader adapter with system/user channel separation.
- Effect on final response: returns validated structured grading result or review/reject.
- Audit events: standard decision events plus `grader_called` and `grader_completed`.
- Retry behavior: bounded adapter retry on timeout/transient provider errors.
- User-visible response: grading result; security notes only if configured.
- Analyst-visible response: adapter version, output validation, score drift metadata.
- Failure behavior: invalid grader output follows failure matrix.
- Prohibited behavior: must not call deterministic demo a real grader benchmark.

## `manual_review`

- Trigger conditions: critical risk, ambiguous high impact, dependency failure, invalid grader output, or policy escalation.
- Required evidence: priority, reason code, redacted evidence, policy version, SLA.
- Effect on input: raw content hidden by default; full content requires permission.
- Effect on grader: grading may be delayed or provisional by integration policy.
- Effect on final response: queued/review-required public status.
- Audit events: standard decision events plus `review_created`, assignment/resolution events.
- Retry behavior: review state uses optimistic locking and version conflict handling.
- User-visible response: stable review message with correlation ID.
- Analyst-visible response: queue item with redacted evidence and timeline.
- Failure behavior: if queue unavailable, reject in enforce unless policy permits retry.
- Prohibited behavior: no silent overwrite, no unaudited resolution, no one-click destructive resolution without confirmation.

## `block`

- Trigger conditions: published policy matches severe malicious content, unauthorized request, unsafe output, or critical failure requiring fail-closed.
- Required evidence: policy ID/version, reason code, detector health, correlation ID.
- Effect on input: no content passed to grader.
- Effect on grader: grader is not called.
- Effect on final response: safe public block message.
- Audit events: standard decision events and blocked reason.
- Retry behavior: retry only when block is due to transient infrastructure and marked retryable.
- User-visible response: stable public reason code; no hidden thresholds or detector internals.
- Analyst-visible response: full policy and redacted evidence.
- Failure behavior: if audit cannot record in enforce, fail according to matrix and alert.
- Prohibited behavior: must not be triggered by a single weak heuristic unless a published policy explicitly permits it.

