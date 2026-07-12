# GradingGuard Architecture

Status labels used below:

- `existing`: present in current repository.
- `partial`: present but incomplete or demo-only.
- `planned`: contracted for later phases.
- `external`: outside this repository.

## 1. High-level system context

```mermaid
flowchart LR
  Candidate[Candidate<br/>external] --> GAU[GAU IELTS<br/>external]
  GAU --> Gateway[GradingGuard Gateway<br/>partial]
  Gateway --> Detectors[Detector Ensemble<br/>partial]
  Gateway --> Policy[Policy Engine<br/>planned]
  Gateway --> Grader[Grader Adapter<br/>partial]
  Gateway --> Audit[Persistent Audit Store<br/>planned]
  Analyst[Security Console<br/>partial] --> Gateway
  Reviewer[Reviewer<br/>planned] --> Gateway
```

## 2. Request decision flow

```mermaid
flowchart TD
  A[GAU IELTS submission<br/>external] --> B[request validation<br/>partial]
  B --> C[normalization/preprocessing<br/>existing]
  C --> D[detector ensemble<br/>partial]
  D --> E[risk aggregation<br/>existing]
  E --> F[policy decision<br/>planned]
  F --> G{selected action}
  G -->|allow/warn| H[protected grader path<br/>partial]
  G -->|sanitize| I[sanitization evidence<br/>partial]
  G -->|secure_grade| J[secure grading flow<br/>partial]
  G -->|manual_review| K[manual review queue<br/>planned]
  G -->|block| L[public safe block response<br/>planned]
  H --> M[normalized outcome<br/>partial]
  I --> M
  J --> M
  K --> M
  L --> M
  M --> N[persistent evidence/audit<br/>planned]
```

## 3. Trust boundaries

```mermaid
flowchart LR
  subgraph U[Untrusted]
    C[Candidate content]
    DS[External datasets]
  end
  subgraph I[Integration boundary]
    G[GAU IELTS client]
  end
  subgraph GG[GradingGuard]
    V[Validator]
    N[Normalizer]
    DE[Detectors]
    PE[Policy]
    AE[Audit events]
  end
  subgraph P[Privileged services]
    GR[Grader/provider]
    AS[Audit storage]
  end
  C --> G --> V --> N --> DE --> PE --> GR
  PE --> AE --> AS
  DS --> V
```

## 4. Detector ensemble

```mermaid
flowchart TD
  Input[normalized content] --> H[heuristic detector<br/>existing]
  Input --> O[obfuscation detector<br/>existing]
  Input --> S[semantic embedding detector<br/>partial/unavailable when dependency missing]
  H --> R[risk aggregation]
  O --> R
  S --> R
  R --> Health[detector health snapshot]
```

## 5. Policy routing

```mermaid
flowchart TD
  Risk[risk + confidence + techniques] --> Policy[policy evaluation<br/>planned]
  Mode[operating mode] --> Policy
  Health[detector health] --> Policy
  Policy --> A[allow]
  Policy --> W[warn]
  Policy --> S[sanitize]
  Policy --> SG[secure_grade]
  Policy --> MR[manual_review]
  Policy --> B[block]
```

## 6. Secure grading flow

```mermaid
flowchart TD
  Content[student content] --> Iso[input isolation]
  Rubric[grader rubric/system prompt] --> Iso
  Iso --> Adapter[grader adapter<br/>partial]
  Adapter --> Validate[structured output validation<br/>planned]
  Validate --> Score[normalized grading result]
  Validate --> Review[manual review on invalid output<br/>planned]
```

## 7. Manual review lifecycle

```mermaid
stateDiagram-v2
  [*] --> pending
  pending --> assigned
  pending --> expired
  assigned --> in_review
  assigned --> escalated
  in_review --> resolved_allow
  in_review --> resolved_block
  in_review --> escalated
  escalated --> assigned
  escalated --> expired
```

## 8. Evidence and audit flow

```mermaid
flowchart LR
  Decision[decision made] --> Event[audit event]
  Event --> Redact[redaction policy]
  Redact --> Store[persistent store<br/>planned]
  Redact --> Export[evidence export<br/>partial]
  Export --> Judge[Judge/Evidence UI<br/>partial]
```

## 9. Degraded-mode flow

```mermaid
flowchart TD
  Health[dependency health check] --> Bad{critical dependency unavailable?}
  Bad -->|no| Normal[configured mode]
  Bad -->|yes| D[degraded mode]
  D --> Reason[reason code + correlation ID]
  Reason --> Matrix[failure-mode matrix]
  Matrix --> Outcome[continue-with-warning / manual_review / retry / reject]
```

## 10. Benchmark/evidence pipeline

```mermaid
flowchart LR
  Source[source registry] --> Canonical[canonical dataset]
  Canonical --> Runner[benchmark runner]
  Runner --> Metrics[metrics report]
  Runner --> Evidence[evidence report]
  Evidence --> ClaimGuard[claim-drift guard]
  Metrics --> UI[Benchmark/Evidence UI]
```

## Runtime path boundaries

- Synchronous path: request validation -> normalization -> detectors -> risk aggregation -> policy/action -> grader/review/block -> public response.
- Asynchronous path: audit persistence, review assignment, evidence export, health telemetry.
- Benchmark-only path: dataset runner, evidence reports, failure analysis.
- Demo-only path: deterministic mock grading and attack arena.
- Future capability: persistent audit, real policy store, RBAC, production grader adapter, manual review backend.

