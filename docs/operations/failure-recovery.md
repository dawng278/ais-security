# Failure Recovery

Phase 4 covers pilot failure behavior for:

- invalid/expired token
- missing permissions
- rate limiting
- stale optimistic-lock update
- missing published policy for enforce mode
- embedding unavailable reported truthfully

Circuit-breaker primitives are present for future external grader/provider adapters. Production retry/backoff tuning remains future work.

