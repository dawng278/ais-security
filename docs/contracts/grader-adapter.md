# Grader Adapter Contract

Status: Phase 1 contract

## Adapter methods

- `grade_clean(content, context)`: grade trusted-normal content without security intervention.
- `grade_protected(content, context, security_decision)`: grade under security controls.
- `health()`: provider health, version, latency, and dependency status.
- `normalize_output(raw_output)`: convert provider output to canonical grading result.
- `timeout()`: enforce request budget.
- `retry()`: bounded retry for transient provider errors.
- `provider_metadata()`: provider name, model/version, adapter version, environment.

## Required semantics

- Input isolation: candidate content must not share the same authority as system instructions.
- System/user channel separation must be maintained by the adapter.
- Structured output validation is mandatory before returning a score.
- Score range validation must reject impossible IELTS bands.
- Rubric validation must ensure the requested task module matches the rubric.
- Refusal handling must distinguish provider safety refusal from invalid output.
- Malformed output follows the gateway error/failure matrix.
- Provider timeout must produce `GRADER_TIMEOUT`.
- Provider versioning must be stored in decision metadata.

## Adapter classes

- `MockGrader`: current simple local mock used by the prototype.
- `DeterministicDemoGrader`: stable demo-only adapter for judge walkthroughs.
- `MeasuredEvaluationGrader`: benchmark adapter used only when methodology and artifacts are defined.
- `ProductionIntegrationAdapter`: future real integration adapter gated by pilot/production readiness.

The deterministic demo must not be described as a real grader benchmark.

