# Manual Review UI

Backed by `/api/v1/security/reviews`.

Implemented:

- assign;
- start review;
- resolve allow;
- resolve block;
- escalate;
- expected-version optimistic locking;
- idempotency keys;
- conflict/error state.

High-impact actions are explicit buttons with server-side authorization and audit semantics.

