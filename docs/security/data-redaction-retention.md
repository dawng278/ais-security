# Data Redaction and Retention Contract

Status: technical proposal; requires organizational and legal approval before pilot or production.

## Sensitive content

- Email, phone, external IDs, candidate identifiers, account IDs.
- API keys, tokens, credentials, model/provider secrets.
- Raw essays and speaking transcripts.
- Grader prompts, rubric internals, private policy conditions.
- Reviewer notes and manual review resolution rationale.
- Evidence spans that reveal sensitive input.

## Default redaction

- Normal logs store request IDs, correlation IDs, pseudonymous IDs, hashes, severity, action, policy version, and detector health.
- Normal logs must not store raw candidate content, full grader prompts, credentials, regex internals, hidden thresholds, or stack traces.
- Analyst UI shows redacted content by default.
- Full-content access requires explicit permission, justification, and `sensitive_content_accessed` audit event.

## Retention classes

| class | examples | default retention | deletion semantics |
|---|---|---|---|
| operational metadata | request ID, action, health | short operational window | delete or aggregate after window |
| security evidence | redacted spans, detector result | competition/pilot evidence window | immutable event retained until policy expiry |
| full sensitive content | raw essay/transcript | minimum necessary | delete on request/retention expiry when legally allowed |
| benchmark data | open/legal datasets, generated cases | project evidence window | keep with source/license metadata |
| reviewer notes | triage notes, resolution | review governance window | append correction, then expire per policy |

## Evidence export rules

- Export redacted evidence by default.
- Include run ID, git commit, dataset hash, config hash, and detector health.
- Label measured, historical, demo, planned, and unavailable states explicitly.
- Do not export raw sensitive content unless policy permits and audit records the actor/reason.

## Benchmark-data exceptions

Open datasets and generated benchmark cases may be retained longer when license registry and lineage records permit it. Exceptions must not be used to retain real candidate content without approval.

## Log rules

- Public errors include a safe message and correlation ID only.
- Internal reason codes are stable and non-secret.
- Stack traces stay in protected internal telemetry, never in public API responses.

