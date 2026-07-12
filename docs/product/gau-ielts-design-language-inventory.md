# GAU IELTS Design-Language Inventory

Reference repo: `/home/dawngbeo/Documents/github-project/gau-ielts`  
Reference HEAD recorded during Phase 1: `f2b7bddf8a24a42e0ded03208e4d92ae3ae166e7`  
Reference status: dirty before Phase 1 with existing Reading-related changes; Phase 1 did not modify the reference repo.

This inventory is read-only and maps GAU IELTS patterns to future GradingGuard security-console work.

| GAU IELTS pattern | Observed source | GradingGuard equivalent | Security extension | Planned implementation area |
|---|---|---|---|---|
| Typography | `globals.css`, `layout.tsx`, Geist/font variables | Use one sans/mono pairing; avoid mixed arbitrary font stacks. | Mono for request IDs, hashes, policy versions. | global shell and evidence panels. |
| Color tokens | `design-tokens.ts`, skill hues, `--pq-*` CSS tokens | Replace ad-hoc dark-only palette with tokenized surfaces. | Add severity tokens: low/medium/high/critical and mode tokens. | security overview, incident detail. |
| Spacing | card padding variables, page shells | Use consistent section gap and card padding. | Dense audit rows use compact spacing, not cramped raw tables. | all console routes. |
| Radius | canonical card/button components | Rounded cards/buttons, predictable focus rings. | Severity badges and mode banners inherit radius scale. | UI kit layer. |
| Shadows | `AISCard`, `Card` elevated variants | Use elevation only for interactive/priority surfaces. | Critical alerts use border/color before shadow. | threat inbox and review queue. |
| Buttons | `AISButton`, `Button` variants | Primary/secondary/ghost/danger variants. | Dangerous actions require confirmation and audit reason. | policy publish/rollback, resolve block. |
| Inputs | rich-text editor, search bar, form controls | Tokenized search/filter inputs. | Redaction-safe textareas and read-only evidence viewers. | playground and incident filters. |
| Cards | `AISCard`, `CardMedia`, `CardBody` | Security metric cards and incident cards. | Cards carry status label: measured/demo/planned/degraded. | dashboard and Judge View. |
| Tables | existing reading/admin data patterns | Use tables for benchmark and audit lists. | Sticky correlation ID, redacted fields by default. | evidence, audit timeline. |
| Dialogs | modal component | Confirm sensitive actions. | Must show action, actor, target, audit event, rollback path. | policy management and review resolution. |
| Drawers | layout patterns | Use detail drawers for incident evidence. | Drawer never reveals raw content without explicit permission. | threat inbox. |
| Navigation | dashboard/admin layouts, top bars | Console sections grouped by security workflow. | Always show mode and detector health near nav. | app shell. |
| Headers | hero/section headers | Page headers with short capability labels. | Include readiness/degraded banners where applicable. | all routes. |
| Icons | `AISIcon`, `PixelIcons`, lucide usage | Prefer one icon abstraction. | Security icons mapped to severity and event types. | UI kit. |
| Breakpoints | Tailwind responsive patterns | Two-column desktop, single-column mobile. | Incident/review actions remain reachable without horizontal scroll. | route layouts. |
| Loading/error/empty | `EmptyState`, `ErrorState`, `Skeleton` | Never blank screens; always show next action. | Degraded state explains dependency and safe behavior. | all async routes. |
| Dark/light support | current GAU token strategy | Keep theme-reactive tokens. | Security colors must pass contrast in both themes. | console theme. |

Mapping rule: do not copy GAU IELTS source into AIS-GAU-SECURITY. Recreate only the design intent through local tokens/components in a later frontend phase.

