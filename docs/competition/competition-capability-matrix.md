# Competition Capability Matrix

| competition requirement | GradingGuard capability | implementation state | evidence required | UI/demo surface | acceptance gate | limitation |
|---|---|---|---|---|---|---|
| AI model security | Gateway detects prompt injection and score manipulation around AI grading. | partial | benchmark report, detector health, attack examples. | Judge View, Attack Arena, Playground. | COMPETITION_READY evidence. | Does not prove complete adversarial robustness. |
| training/data integrity | Dataset lineage, source registry, evidence hashes. | partial | source registry, license registry, dataset hash. | Data Lineage, Evidence. | claim-drift guard passes. | No new Phase 1 dataset implementation. |
| threat detection | Rule/obfuscation/semantic detector contract. | partial | v3 benchmark and detector-interface contract. | Dashboard, Playground. | benchmark reproducible. | Embedding unavailable if dependencies missing. |
| incident response | Manual review workflow and audit events. | planned | workflow contract, later persistent queue. | planned Threat Inbox/Manual Review Queue. | PILOT_READY. | Backend not implemented in Phase 1. |
| score integrity | Secure grading and verifier concept. | partial/demo | score drift methodology and adapter metadata. | Judge View, Compare/Attack Arena. | Score Integrity track. | Mock grader is not a real measured grader. |
| explainability | Evidence card/report, detected patterns, action semantics. | partial | evidence artifacts, action contract. | Evidence, Judge View. | public claims match artifacts. | Public output must redact internals. |
| operational reliability | Mode and failure matrix contract. | planned | fault-injection tests later. | Integration & Runtime, Detector Health. | Operational Reliability track. | No production telemetry yet. |
| misconfiguration detection if applicable | Policy validation, mode transition gates. | planned | policy validation tests. | Policy Management. | PILOT_READY. | No policy store in Phase 1. |
| reproducibility | Phase reports, checksums, deterministic contract validation. | existing/partial | pytest, frontend build, claim guard, protected checksums. | Evidence. | Phase 1 validation passes. | Docker remains unverified. |
| GAU IELTS integration | Contracted gateway request/decision/error schemas and GAU design inventory. | planned/contracted | schemas, API contract, design inventory. | Integration & Runtime planned. | Pilot integration gate. | GAU repo is read-only. |

