# Redaction and Retention

Redaction covers:

- email
- phone
- bearer tokens
- API keys
- secret-like values

Default list/detail responses expose safe previews and hashes, not raw candidate content. Sensitive evidence access requires permission and audit.

Retention is implemented as dry-run only in Phase 4. The dry-run reports eligible record counts by category and performs no destructive action.

