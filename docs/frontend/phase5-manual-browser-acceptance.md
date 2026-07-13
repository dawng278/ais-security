# Phase 5 Manual Browser Acceptance Checklist

Status: `NOT_RUN`

This checklist must be completed by a human verifier in a genuinely visible headed browser session before Phase 5 can be promoted to `DONE`.

## Required setup

- Start the Phase 5 E2E backend with isolated `TEST_DATABASE_URL`.
- Start the Phase 5 frontend on the dedicated E2E port.
- Use a visible headed Chromium/Chrome browser.
- Set browser zoom through browser chrome controls or browser-level keyboard shortcuts to exactly `200%`.
- Do not use CSS zoom, `transform: scale()`, device scale factor, screenshots, or headless assertions as substitutes.

## Record before testing

- Verifier:
- Verified at:
- Browser:
- Browser version:
- OS:
- Display resolution:
- Viewport before zoom:
- Zoom percent: `200%`

## 200% zoom routes

Mark each route `PASS`, `FAIL`, or `NOT_RUN`.

- `/dashboard`
- `/threat-inbox`
- `/incidents/[id]`
- `/manual-review`
- `/policies`
- `/detector-health`
- `/benchmark`
- `/evidence`
- `/data-lineage`
- `/integration-runtime`
- `/attack-arena`
- `/judge-view`
- `/playground`

For each route verify:

- AppShell is usable.
- skip link is reachable.
- navigation is reachable.
- no critical content overlaps.
- no critical action is clipped.
- operating mode and production-readiness limitation remain visible.
- dialogs and action controls remain within the visible viewport.
- focus remains visible.
- no page-level horizontal scroll exists except contained keyboard-scrollable data grids.

## Keyboard-only flows

After initial browser setup, complete without mouse:

- skip link
- AppShell navigation
- compact/mobile drawer if triggered
- Threat Inbox filters
- table/detail navigation
- Incident Detail restricted reveal
- Manual Review assignment/state transition
- optimistic conflict presentation
- policy validation/publish/rollback controls
- Detector Health reading path
- Benchmark/Evidence reading path
- Attack Arena run controls
- Judge View narrative controls
- Escape behavior
- Enter/Space activation
- visible focus
- no keyboard trap
- success/error announcements

## Attestation

Manual acceptance remains `NOT_RUN` until this checklist is completed and copied into:

- `datasets/evidence/phase5/phase5_frontend_security_console/manual_browser_acceptance.json`

Do not mark Phase 5 `DONE` without a verifier and completed checklist.
