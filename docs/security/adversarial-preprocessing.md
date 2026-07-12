# Adversarial Preprocessing

Phase 3 hardens normalization without changing canonical dataset membership.

Capabilities:

- Unicode NFKC normalization.
- Zero-width removal.
- Bidirectional-control removal.
- Control-character handling.
- HTML entity normalization.
- URL-encoded evidence detection.
- Bounded Base64 text decoding.
- Maximum decoded size and nested-depth limits.
- Code/delimiter flagging.

Security constraints:

- Original input remains preserved by callers.
- Decoded text is appended only to analysis input and never executed.
- Binary/oversized decoded payloads are rejected.
- Normalization flags are evidence metadata, not public exploit detail.

