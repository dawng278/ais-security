# ADR-011 Phase 5 Waiver and Phase 6 Authorization

Status: accepted

## Context

Phase 5 frontend implementation is complete and verified on the runnable local browser projects:

- Chromium desktop
- Firefox desktop
- Android mobile emulation
- Chromium tablet

The remaining Phase 5 gates are not implementation blockers in the current environment:

- `webkit-desktop`: `BLOCKED_HOST_DEPENDENCIES`
- `mobile-ios`: `BLOCKED_HOST_DEPENDENCIES`
- actual headed-browser zoom at 200%: `NOT_RUN`
- manual keyboard-only acceptance: `NOT_RUN`

The project must not convert blocked or not-run gates into `PASS`, but it also should not keep Phase 6 blocked when the remaining work is environment and human-verification debt.

## Decision

Accept Phase 5 implementation for Phase 6 progression under an environmental verification waiver.

The formal Phase 5 verdict remains:

```text
PHASE_5_FRONTEND_SECURITY_CONSOLE_PARTIAL
```

The implementation acceptance state is:

```text
PHASE_5_IMPLEMENTATION_ACCEPTED_WITH_ENVIRONMENTAL_WAIVER
VERIFICATION_DEBT: OPEN
PHASE_6: AUTHORIZED
PRODUCTION_READY: NOT_READY
```

Outstanding browser and manual acceptance gates remain mandatory before final competition submission or any production-readiness review.

## Alternatives considered

- Keep Phase 6 blocked until WebKit and human manual acceptance can run.
- Mark Phase 5 `DONE` despite blocked/not-run gates.
- Remove WebKit/manual gates from the acceptance policy.

## Consequences

Phase 6 may begin with deployment, reproducibility and environment hardening.

Phase 6 may include a reproducible Playwright WebKit container environment intended to close Phase 5 verification debt later, but it must not claim Docker or WebKit support as verified until the workflow actually runs and passes.

Reports and evidence must continue to show:

```text
webkit-desktop: BLOCKED_HOST_DEPENDENCIES
mobile-ios: BLOCKED_HOST_DEPENDENCIES
actual 200% headed zoom: NOT_RUN
manual keyboard-only acceptance: NOT_RUN
```

## Later-phase implementation impact

Phase 6 should prioritize:

- reproducible setup documentation;
- isolated E2E environment contracts;
- Docker/test-container artifacts clearly labeled as test-only until verified;
- environment audit scripts;
- evidence refresh workflows that preserve Phase 5 verification debt truthfully.
