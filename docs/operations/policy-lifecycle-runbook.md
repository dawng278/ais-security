# Policy Lifecycle Runbook

Phase 4 persists policy versions.

Lifecycle:

1. Policy manager creates a validated draft.
2. Security admin publishes a validated version.
3. Publishing supersedes the previous active version for that policy.
4. Security admin can rollback to a known version.

Published versions are not edited in place. Policy documents are JSON only; no Python, eval or arbitrary code execution is allowed.

