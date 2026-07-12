# GradingGuard AI Product Contract

Status: frozen for Phase 1  
Scope: product and architecture contract only

## Mission

GradingGuard AI is a security gateway around AI-assisted IELTS-style grading. It analyzes candidate submissions before grading, selects a policy action, preserves evidence, and helps analysts understand attempts to manipulate grading outcomes.

The product is not an IELTS certification authority, not a guarantee against every adversarial attack, and not production-ready merely because the deterministic demo succeeds.

## Protected assets

- Candidate submission content.
- Grader system instructions and rubric.
- Grading outcome and score integrity.
- Detector models, detector configuration, and policy configuration.
- Decision evidence, audit records, benchmark artifacts, and reviewer actions.
- Model/provider credentials and integration secrets.

## Primary users

- GAU IELTS integration service: sends candidate submissions and receives safe grading decisions.
- Security analyst: investigates threats, evidence, detector health, and incidents.
- Reviewer: resolves manual review items without seeing raw sensitive content by default.
- Policy manager: proposes, validates, publishes, rolls back, and archives security policy.
- Security administrator: controls mode changes, permissions, retention, and operational readiness.
- Competition judge/demo viewer: reviews honest capability evidence and reproducible demo surfaces.

## Supported use cases

- Detect prompt-injection, role-spoofing, obfuscation, and score-manipulation attempts in grading submissions.
- Select one of the contracted actions: `allow`, `warn`, `sanitize`, `secure_grade`, `manual_review`, or `block`.
- Provide a controlled rollout path through `shadow`, `warn`, `enforce`, and `degraded` modes.
- Preserve evidence and audit metadata for analyst review and benchmark reproducibility.
- Demonstrate competition value with current prototype capabilities while labeling mock/demo/runtime gaps honestly.

## Explicitly unsupported use cases

- Certifying official IELTS scores.
- Making legal, disciplinary, or admissions decisions without human governance.
- Claiming exhaustive adversarial robustness.
- Running production enforce mode without auth/RBAC, persistent audit, rollback, privacy review, and operational ownership.
- Treating deterministic demo grading as a measured real grader benchmark.
- Installing paid APIs, large models, or new datasets in Phase 1.

## Trust assumptions

- GAU IELTS integration sends authenticated and authorized traffic in later phases; Phase 1 only defines the contract.
- Candidate text is untrusted.
- External datasets and benchmark inputs are untrusted until lineage and licensing checks pass.
- Detector output is advisory until policy evaluation and audit succeed.
- Analyst console users require RBAC in later phases.
- Public responses must not reveal secrets, hidden thresholds, system prompts, raw sensitive evidence, or detector internals.

## Operating environments

- Local prototype: current FastAPI and Next.js application with deterministic demo surfaces.
- Competition demo: reproducible, evidence-backed, clearly labeled as demo/measured/planned.
- Pilot: shadow/warn integration with persistent audit, auth/RBAC, redaction, rollback, and review workflow.
- Production: enforce-mode eligible only after pilot evidence, security/privacy review, load testing, disaster recovery, and validated grader integration.

## Current prototype boundaries

- Existing runtime actions are `allow`, `warn`, `secure_grade`, and `manual_review`.
- `sanitize` and `block` are Phase 1 contracted semantics for later implementation, not current runtime behavior.
- Embedding detector must be reported as unavailable when `sentence-transformers` is missing.
- Docker deployment remains unverified.
- Persistent audit storage, policy versioning, manual review backend, auth/RBAC, and production integration are later-phase gaps.

## Business outcomes

- Reduce grading manipulation and score inflation.
- Preserve score integrity and rubric separation.
- Expose evidence for review instead of silent decisions.
- Support analyst/reviewer workflows.
- Enable controlled rollout without overclaiming readiness.
- Avoid silently degrading grading availability when dependencies fail.

