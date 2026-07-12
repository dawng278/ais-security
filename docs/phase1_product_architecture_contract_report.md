# Phase 1 Product and Architecture Contract Report

Verdict: `PHASE_1_PRODUCT_ARCHITECTURE_CONTRACT_DONE`

Date: 2026-07-13  
Repository: `/home/dawngbeo/school-project/ais-gau-security`  
Phase 0 baseline HEAD: `8c93f87440d3ae8a7805765e3498b02d1d8235c1`

## Preflight

- Branch: `main`.
- Existing protected dirty files were classified as `USER_EXISTING_WORK`.
- GAU IELTS reference repo was read-only and already dirty before Phase 1.
- No Docker, dataset, detector tuning, auth/RBAC, DB migration, or frontend redesign work was started.

## Protected report checksums

Before and after Phase 1:

```text
863c8509af20d56e4f1370948f3ebf8b11562efef59245ab5e71061b83f44003  datasets/reports/v3/benchmark_v3_combined.json
c9e60724e1e8d6ba53549e790222e4a1f6e6e8cad8d74fb7001b62dfe9e9071f  datasets/reports/v3/evidence/evidence_card.md
c5aa5b41c602c299acb59d8a0097e22aee12ed4d2a5ee8d06b5aa3bacf937b67  datasets/reports/v3/evidence/evidence_report.json
```

Result: unchanged.

## Documents and contracts created

- Product contract: `docs/product/gradingguard-product-contract.md`
- Readiness gates: `docs/product/readiness-gates.md`
- Security console IA: `docs/product/security-console-information-architecture.md`
- GAU IELTS design inventory: `docs/product/gau-ielts-design-language-inventory.md`
- Threat model: `docs/security/threat-model.md`
- Threat-control-test matrix: `docs/security/threat-control-test-matrix.md`
- Redaction/retention proposal: `docs/security/data-redaction-retention.md`
- Architecture diagrams: `docs/architecture/gradingguard-architecture.md`
- Operating modes/failure matrix: `docs/architecture/operating-modes.md`
- Action semantics: `docs/architecture/action-semantics.md`
- Machine-readable contract: `docs/architecture/gradingguard_architecture_contract.json`
- Gateway API/error contract: `docs/contracts/grading-gateway-api.md`
- Detector interface: `docs/contracts/detector-interface.md`
- Policy contract/lifecycle: `docs/contracts/policy-contract.md`
- Grader adapter contract: `docs/contracts/grader-adapter.md`
- Audit event contract: `docs/contracts/audit-event-contract.md`
- Manual review workflow: `docs/contracts/manual-review-workflow.md`
- Benchmark tracks: `docs/benchmark/benchmark-track-contracts.md`
- Competition capability matrix: `docs/competition/competition-capability-matrix.md`
- ADR-001 through ADR-010.
- JSON schemas: `schemas/grading_request.schema.json`, `schemas/grading_decision.schema.json`, `schemas/grading_error.schema.json`.
- Validation tests: `backend/tests/test_architecture_contract.py`.

## Semantic conflicts found

- Current backend runtime supports `allow`, `warn`, `secure_grade`, and `manual_review`.
- Phase 1 product contract requires future actions `sanitize` and `block`.
- Resolution: contract freezes all six actions, while `runtime_action_state` explicitly labels `sanitize` and `block` as planned.
- Current embedding runtime can be unavailable when dependencies are missing.
- Resolution: detector health contract forbids calling embedding `healthy` unless dependencies/model are actually available.

## Decisions made

- GradingGuard is a security gateway, not an IELTS certification authority.
- Modes are frozen as `shadow`, `warn`, `enforce`, and `degraded`.
- Actions are frozen as `allow`, `warn`, `sanitize`, `secure_grade`, `manual_review`, and `block`.
- Benchmark claims are split into four tracks: generic prompt injection, IELTS domain security, score integrity, and operational reliability.
- Deterministic demo grading remains separate from measured grader evidence.
- GAU IELTS is a read-only design/integration reference.

## Coverage

- Threats covered: 24/24.
- Required audit events covered: 16/16.
- Review states reachable from `pending`: 7/7.
- Error codes unique and documented: 15/15.
- Frontend IA routes covered: 13/13.
- ADRs complete: 10/10.

## Verification

Commands run:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=backend:. python -m pytest backend/tests -q
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/eslint
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/tsc --noEmit
PATH=/home/dawngbeo/.cache/ms-playwright-go/1.57.0:$PATH ./node_modules/.bin/next build
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. python scripts/audit_public_claims.py
git diff --check
```

Results:

- Backend tests: 41 passed.
- Contract validation tests: 8 passed.
- Frontend lint: PASS.
- Frontend typecheck: PASS.
- Frontend build: PASS.
- Claim-drift guard: PASS, 0 findings.
- `git diff --check`: PASS.
- Protected report checksum comparison: PASS.
- GAU IELTS HEAD unchanged: `f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7`.
- GAU IELTS dirty status unchanged from preflight; no reference repo edits were made.

## Blockers and warnings

Blockers: none for Phase 1.

Warnings:

- Pilot and production readiness remain blocked by later-phase implementation work: auth/RBAC, persistent audit, policy store, manual review backend, real grader integration, observability, backup/restore, and privacy/security review.
- Docker remains outside Phase 1 and unverified.
- Phase 2 is not automatically authorized by this report; it can start only after user approval.

## Unresolved architecture decisions

Unresolved critical architecture decisions: 0.

