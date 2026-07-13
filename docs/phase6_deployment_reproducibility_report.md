# Phase 6 Deployment, Reproducibility & Environment Hardening Report

Status: `PHASE_6_STARTED`

Phase 6 is authorized by `ADR-011` under an environmental verification waiver:

```text
PHASE_5_FORMAL_VERDICT: PARTIAL
PHASE_5_IMPLEMENTATION: ACCEPTED
VERIFICATION_DEBT: OPEN
PHASE_6: AUTHORIZED
PRODUCTION_READY: NOT_READY
```

## Initial hardening scope

- Preserve Phase 5 blocked/not-run evidence truthfully.
- Add a reusable WebKit test-container artifact without claiming it is verified in this local environment.
- Add an external-server mode to the Playwright config so browser containers can run against host-started isolated E2E services.
- Add an environment audit script for reproducibility and deployment readiness.

## Current local environment result

Docker CLI is unavailable in the current environment, so Docker build/run verification remains `NOT_RUN`.

The Playwright WebKit test image is test-only:

```text
frontend/e2e/Dockerfile.playwright-webkit
base image: mcr.microsoft.com/playwright:v1.61.1-noble
```

No production deployment claim is made.

## Verification debt retained

```text
webkit-desktop: BLOCKED_HOST_DEPENDENCIES
mobile-ios: BLOCKED_HOST_DEPENDENCIES
actual headed-browser zoom 200%: NOT_RUN
manual keyboard-only acceptance: NOT_RUN
```

## Next closure command on a suitable environment

Start isolated host backend/frontend first, then run the test-only container with host networking:

```bash
docker build -f frontend/e2e/Dockerfile.playwright-webkit -t ais-gau-security-playwright-webkit:1.61.1 .
docker run --rm --init --ipc=host --network host \
  -e PHASE5_E2E_EXTERNAL_SERVERS=1 \
  -e NEXT_PUBLIC_API_URL=http://127.0.0.1:18100 \
  ais-gau-security-playwright-webkit:1.61.1
```

Only after WebKit/iOS pass and a human verifier completes the manual browser checklist may Phase 5 be promoted to `DONE`.
