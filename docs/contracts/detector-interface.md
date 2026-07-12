# Detector Interface Contract

Status: Phase 1 contract

## Input

Every detector receives:

- `normalized_content`: normalized candidate content.
- `task_type`: writing or speaking.
- `language`: request language.
- `context`: safe grader/module metadata.
- `content_length`: length after normalization.
- `correlation_id`: trace ID.
- `timeout_budget_ms`: detector-specific budget.

## Output

Every detector returns:

- `detector_id`.
- `detector_version`.
- `runtime_state`: `healthy`, `warming`, `degraded`, `unavailable`, or `disabled`.
- `risk_contribution`: 0..1.
- `confidence`: 0..1.
- `detected_techniques`.
- `evidence_spans`: redacted or span-reference based.
- `latency_ms`.
- `warnings`.
- `error_reason`.

## Health model

Health state dimensions must remain separate:

- `configured_state`: enabled/disabled by configuration.
- `dependency_state`: dependency available/missing/failed.
- `model_load_state`: not_attempted/not_loaded/loaded/failed.
- `runtime_state`: `healthy`, `warming`, `degraded`, `unavailable`, `disabled`.

Embedding detector rule: when `sentence-transformers` is unavailable, embedding must not be called `healthy`; it is `unavailable` with a fallback reason.

## Runtime semantics

- Detector errors must be bounded by timeout and transformed into detector output with `runtime_state`.
- Detectors must not throw raw stack traces into public API responses.
- Evidence spans must be references or redacted snippets by default.
- Risk aggregation may use detector output only after normalizing health and confidence.

