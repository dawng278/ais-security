# Deployment, Reproducibility and Environment Hardening Runbook

Status: `PHASE_6A_NON_DOCKER_READY`

This runbook covers the Phase 6A work that can be completed without a local Docker runtime. It does not claim Docker deployment support.

## 1. Static validation gate

Run from the repository root:

```bash
python3 scripts/phase6_static_validation.py
python3 scripts/audit_public_claims.py
python3 scripts/phase6_environment_audit.py
```

Expected current result:

```text
phase6_static_validation: PASS
public_claim_audit: PASS
phase6_environment_audit: PHASE_6_STARTED_ENVIRONMENT_HARDENING_PARTIAL
docker: UNAVAILABLE
production: NOT_READY
```

## 2. Startup validation checklist

Before any non-development run:

1. Copy `backend/.env.example` and `frontend/.env.example` into environment-specific secret stores.
2. Replace `AUTH_TOKEN_SECRET=development-only-change-me` with a long random value.
3. Confirm `CORS_ALLOWED_ORIGINS` contains only expected frontend origins.
4. Confirm `SECURITY_DATABASE_URL` points to the intended environment.
5. Keep `TEST_DATABASE_URL` empty outside isolated automated tests.
6. Confirm `NEXT_PUBLIC_API_URL` points to the intended backend.

## 3. Health and readiness contract

Use the existing health/readiness surfaces:

```text
/health
/api/v1/security/health/live
/api/v1/security/health/ready
/api/v1/security/runtime
```

Readiness must remain truthful about:

- database reachability;
- runtime mode;
- audit persistence;
- embedding availability;
- degraded/unavailable dependencies.

## 4. Artifact retention

Keep Playwright traces, screenshots and HTML reports out of Docker build contexts and commits.

Allowed retention locations:

```text
frontend/.playwright-artifacts/
frontend/playwright-report/
frontend/test-results/
datasets/evidence/phase6/
```

Only evidence summaries intended for audit should be committed.

## 5. Backup and rollback plan

For the current prototype:

- canonical benchmark/evidence files are preserved by checksum;
- generated Phase 6 evidence is reproducible through `scripts/phase6_environment_audit.py`;
- rollback is Git-based for source/config changes;
- database backup/restore remains a documented requirement before any production-readiness review.

Do not run destructive Docker cleanup, volume prune or database reset as part of Phase 6A.

## 6. Docker/WebKit closure path

On a separate environment with Docker available:

```bash
docker build -f frontend/e2e/Dockerfile.playwright-webkit -t ais-gau-security-playwright-webkit:1.61.1 .
docker run --rm --init --ipc=host --network host \
  -e PHASE5_E2E_EXTERNAL_SERVERS=1 \
  -e NEXT_PUBLIC_API_URL=http://127.0.0.1:18100 \
  ais-gau-security-playwright-webkit:1.61.1
```

Then run the full six-project browser matrix and complete the human manual browser acceptance checklist. Until that happens:

```text
DOCKER_VERIFIED=false
WEBKIT_VERIFIED=false
PRODUCTION_READY=NOT_READY
```
