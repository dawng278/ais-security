# GAU IELTS Gateway Integration

Phase 4 adds a versioned pilot API under `/api/v1/security`.

Integration flow:

1. GAU-style service obtains a signed integration token.
2. It submits `grading_request.v1` to `/api/v1/security/analyze` or `/grade`.
3. GradingGuard runs Phase 3 detectors and policy in the persisted operating mode.
4. The gateway persists decision, detector summaries, audit events, and optional incident/review records.
5. In `shadow` mode, the original grading path remains authoritative; GradingGuard returns the counterfactual action only.

Do not modify the GAU IELTS repository for Phase 4. Use fixtures or adapters inside AIS-GAU-SECURITY until a production integration phase is explicitly authorized.

