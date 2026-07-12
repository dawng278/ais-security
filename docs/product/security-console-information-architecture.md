# Security Console Information Architecture

This document defines planned frontend information architecture only. It does not redesign the current UI in Phase 1.

Route keys intentionally match `docs/architecture/gradingguard_architecture_contract.json`.

| route key | surface | primary user | job to be done | backend data required | current status | required states | permissions | label rules | main actions | mobile behavior |
|---|---|---|---|---|---|---|---|---|---|---|
| `security_overview` | Security Overview | analyst, admin | Understand current risk, mode, health, and evidence freshness. | stats, mode, detector health, latest evidence. | partial via `/dashboard`. | empty/loading/error/degraded. | analyst read. | measured vs demo vs planned. | drill into incidents, benchmark, health. | stacked cards, sticky status banner. |
| `threat_inbox` | Threat Inbox | analyst | Triage risky submissions and trends. | incidents, decisions, severity, actions. | planned. | empty/loading/error/degraded. | analyst read. | live/persistent label required. | filter, assign, open incident. | list-first, filters collapse. |
| `incident_detail` | Incident Detail | analyst, reviewer | Explain one decision and its evidence safely. | decision, redacted evidence, audit trail. | planned. | empty/loading/error/degraded. | analyst/reviewer scoped. | redacted/full-content state. | add note, escalate, export evidence. | tabs become sections. |
| `manual_review_queue` | Manual Review Queue | reviewer | Resolve `manual_review` items with audit. | review items, SLA, lock version, notes. | planned. | empty/loading/error/degraded. | reviewer write. | raw content hidden by default. | assign, resolve allow/block, escalate. | queue cards, confirm actions. |
| `policy_management` | Policy Management | policy manager | Draft, validate, publish, rollback policy. | policy list, versions, validation results. | planned. | empty/loading/error/degraded. | policy admin. | draft/published/rolled_back state. | validate, publish, rollback. | read-first, publish disabled on small accidental taps. |
| `detector_health` | Detector Health | analyst, admin | See detector runtime states and degradation reasons. | detector status, latency, dependency state. | planned. | empty/loading/error/degraded. | analyst read/admin config. | healthy/warming/degraded/unavailable/disabled. | inspect, rerun health check. | compact status rows. |
| `benchmark` | Benchmark | judge, analyst | Review measured benchmark metrics and limitations. | benchmark v3 reports, track metadata. | existing `/benchmark`. | empty/loading/error/degraded. | public demo/read. | measured/historical/planned. | inspect failures, export summary. | metric cards then tables. |
| `evidence` | Evidence | judge, analyst | Inspect latest evidence artifact safely. | evidence report/card, run context. | existing `/evidence`. | empty/loading/error/degraded. | public demo/read. | current/historical/unavailable. | copy run ID, inspect hashes. | collapsible JSON blocks. |
| `data_lineage` | Data Lineage | analyst, judge | Understand source legality and lineage. | source registry, license registry. | existing `/data-lineage`. | empty/loading/error/degraded. | public demo/read. | verified/unverified. | inspect source. | cards by source. |
| `integration_runtime` | Integration & Runtime | admin | Configure client integration, modes, rate limits. | clients, mode, API status, CORS config. | planned. | empty/loading/error/degraded. | admin. | environment and readiness labels. | rotate key, change mode with confirmation. | read-only summary first. |
| `attack_arena` | Attack Arena | judge, analyst | Demonstrate adversarial cases. | attack templates, analyzer result. | existing `/attack-arena`. | empty/loading/error/degraded. | demo/read. | deterministic demo label. | run scenario, compare result. | single-column runner. |
| `judge_view` | Judge View | judge | See the story, metrics, and proof quickly. | curated evidence, benchmark, demo stats. | existing `/judge-view`. | empty/loading/error/degraded. | public demo/read. | honest measured/planned labeling. | start demo path. | hero + evidence cards. |
| `playground` | Playground | developer, judge | Try analyzer on custom text. | firewall analyze API. | existing `/playground`. | empty/loading/error/degraded. | demo/read. | not a production grader label. | analyze, clear, copy result. | text area first. |

Frontend must align with GAU IELTS spacing, cards, buttons, state components, and tone while adding security-specific surfaces such as mode banners, severity badges, evidence panels, and audit timelines.

