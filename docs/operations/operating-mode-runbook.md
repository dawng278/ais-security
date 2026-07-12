# Operating Mode Runbook

Persisted modes:

- `shadow`
- `warn`
- `enforce`
- `degraded`

Mode changes require `security_admin`, confirmation, justification and expected current version.

`enforce` cannot activate without a published policy. This prevents accidental hard enforcement on an unversioned policy state.

Shadow mode remains the first real integration path.

