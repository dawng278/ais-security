# Phase 5 GAU Design Alignment

Reference repository: `/home/dawngbeo/Documents/github-project/gau-ielts`  
Reference HEAD: `f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7`  
Use: read-only design reference.

| GAU IELTS token/pattern | GradingGuard implementation | Security extension | Source file | Rationale |
|---|---|---|---|---|
| Clean learning dashboard shell | Responsive security AppShell with grouped navigation | Mode, readiness, role and production-not-ready badges | `frontend/src/components/AppShell.tsx` | Looks like GAU ecosystem rather than hacker terminal. |
| Card-first layouts | White cards, rounded surfaces, soft borders | Severity/status chips and audit panels | `frontend/src/app/globals.css`, `SecurityConsole.tsx` | Keeps dense security data readable. |
| Geist sans/mono pairing | Existing Next font variables retained | Mono for hashes, IDs, policy versions | `frontend/src/app/layout.tsx` | Matches existing app typography. |
| Soft blue/teal learning palette | `--gg-*` CSS variables | critical/high/medium/low, degraded, unavailable, demo tokens | `frontend/src/app/globals.css` | Security meaning without neon styling. |
| Dashboard navigation patterns | Operations/Governance/Demonstration groups | Permission-aware route visibility | `AppShell.tsx` | Maps to Phase 1 IA and Phase 4 RBAC. |
| Loading/empty/error components | Shared `StatePanel` | unauthorized, forbidden, conflict, rate-limited, degraded, offline | `SecurityConsole.tsx` | No blank page or swallowed backend failure. |
| Modal/drawer intent | Mobile navigation drawer | Focusable drawer controls and skip link | `AppShell.tsx` | Accessible responsive shell. |
| Tables and cards | Incident table + responsive cards/metrics | No raw content in lists | `SecurityConsole.tsx` | Safe analyst triage. |
| Badges | Truth/status labels | LIVE, MEASURED, DETERMINISTIC_DEMO, LOW_SUPPORT, NOT_MEASURED | `SecurityConsole.tsx` | Prevents demo/live confusion. |
| Icon usage | Existing lucide icon system | No second icon library | `AppShell.tsx`, `SecurityConsole.tsx` | One icon system; no arbitrary SVG/emoji controls. |

Phase 5 recreates design intent locally. It does not copy GAU IELTS source files.

