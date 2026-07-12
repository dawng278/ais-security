# Policy Contract and Lifecycle

Status: Phase 1 contract

## Policy structure

A policy contains:

- `policy_id`.
- `name`.
- `version`.
- `status`: `draft`, `validated`, `published`, `superseded`, `rolled_back`, or `archived`.
- `description`.
- `operating_modes`.
- `conditions`.
- `action`: one of the supported actions.
- `priority`.
- `fallback`.
- `created_by`.
- `approved_by`.
- `created_at`, `updated_at`, `published_at`.
- `checksum`.

Policies must not permit arbitrary code execution.

## Lifecycle

```mermaid
flowchart LR
  draft --> validated
  validated --> published
  published --> active
  active --> monitored
  monitored --> superseded_or_rolled_back
  superseded_or_rolled_back --> archived
```

Detailed steps:

1. `draft`: policy created but cannot affect runtime.
2. Validate: schema, condition syntax, action compatibility, and fallback.
3. Test against samples: positive and hard-negative samples.
4. Approval: authorized policy manager and security admin.
5. `published`: immutable version available for activation.
6. Activate: selected for an operating mode.
7. Monitor: audit actions and detector health.
8. Rollback/supersede: replace with previous or newer published version.
9. `archived`: not active, retained for audit.

## Conflict resolution

- Higher `priority` evaluates first.
- Ties resolve by stricter action rank: `block`, `manual_review`, `secure_grade`, `sanitize`, `warn`, `allow`.
- If two policies produce conflicting fallbacks, the policy set is invalid.
- Invalid policy behavior: reject publication; in enforce mode use last known published policy or fail according to the failure matrix.

## Permission boundaries and audit

- Drafting requires policy write permission.
- Publishing requires approval permission.
- Rollback requires confirmation and `policy_rolled_back` audit event.
- Publish requires `policy_published` audit event.
- Mode activation requires `mode_changed` audit event.

