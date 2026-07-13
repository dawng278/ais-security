# Environment Contract

Status: `PHASE_6A_LOCKED_STATIC_CONTRACT`

This contract defines the minimum reproducible environment for GradingGuard AI. It is intentionally stricter than the current local host so the project can distinguish between implementation state and environment debt.

## Runtime profiles

| Profile | Purpose | Verdict allowed |
| --- | --- | --- |
| `development` | Local development and demo iteration | `READY_WITH_ENVIRONMENTAL_WAIVER` |
| `test` | Isolated automated tests with disposable state | `READY_WITH_ENVIRONMENTAL_WAIVER` |
| `competition-submission` | Final judged submission bundle | `NOT_READY` until WebKit/iOS and human browser gates pass |
| `production` | Real deployment handling real user data | `NOT_READY` |

## Required backend variables

The backend environment must provide the variables shown in `backend/.env.example`.

Non-development reviews must fail-fast if:

- `AUTH_TOKEN_SECRET` is empty or still `development-only-change-me`;
- `SECURITY_DATABASE_URL` points at an unintended shared/local database;
- `CORS_ALLOWED_ORIGINS` includes wildcard origins;
- request-size and rate-limit values are missing;
- `TEST_DATABASE_URL` is reused outside an isolated test profile.

## Required frontend variables

The frontend environment must provide `NEXT_PUBLIC_API_URL`.

Phase 5/6 E2E runners may additionally use:

- `PHASE5_E2E_FRONTEND_PORT`
- `PHASE5_E2E_BACKEND_PORT`
- `PHASE5_E2E_EXTERNAL_SERVERS`
- `PHASE5_E2E_NODE_BIN_DIR`

`PHASE5_E2E_EXTERNAL_SERVERS=1` means Playwright must not start nested servers and should connect to externally started isolated backend/frontend services.

## Pinned toolchain expectations

| Component | Expected version |
| --- | --- |
| Node | `v20.19.2` for local pinned runner evidence |
| Next.js | `16.2.10` |
| React / React DOM | `19.2.4` |
| Playwright | `1.61.1` |
| Playwright Docker base | `mcr.microsoft.com/playwright:v1.61.1-noble` |
| Axe Playwright | `4.12.1` |

The Playwright package version and Docker base tag must stay in lockstep. A matching Dockerfile is not evidence that WebKit passed; only a real container run can close the WebKit/iOS verification debt.

## Build-context boundary

The root `.dockerignore` must exclude:

- local dependency folders;
- Next.js build output;
- Playwright traces, screenshots, reports and local E2E databases;
- Python cache folders;
- generated evidence/report bundles;
- secrets and logs.

The Phase 6 WebKit Dockerfile is test-only and must not be reused as a production deployment image.

## Readiness truth table

| Capability | Current status |
| --- | --- |
| Phase 5 formal verdict | `PHASE_5_FRONTEND_SECURITY_CONSOLE_PARTIAL` |
| Phase 5 implementation | `ACCEPTED_WITH_ENVIRONMENTAL_WAIVER` |
| Verification debt | `OPEN` |
| Docker runtime | `UNAVAILABLE` in current local environment |
| Docker deployment verified | `false` |
| WebKit container execution | `NOT_RUN` |
| Competition submission | `NOT_READY` |
| Production readiness | `NOT_READY` |
