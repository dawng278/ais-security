# System Architecture & Pipeline Specifications

> **Technical Diagram Specifications for GradingGuard AI**

---

## 1. Runtime Defense Pipeline

```mermaid
flowchart TD
    A[Student Submission] --> B[Input Normalizer]
    B --> C[Prompt Injection Detector]
    C --> D[Risk Scoring Engine]
    D --> E{Action Decision}
    E -->|Allow / Warn| F[Secure IELTS Grader]
    E -->|Secure Grade| G[AI Grading Sanitizer]
    E -->|Manual Review| H[Manual Review Queue]
    G --> F
    F --> I[Score Integrity Verifier]
    I --> J[Evidence Log]
```

---

## 2. Attack Arena Scenario Flow

```mermaid
flowchart LR
    A[Select Attacker Profile] --> B[Generate Multi-Attempt Payload]
    B --> C[Execute Unprotected Grader]
    B --> D[Execute GradingGuard AI Gateway]
    C --> E[Unprotected Score]
    D --> F[Risk Score & Action Allocation]
    F --> G[Sanitized Text]
    G --> H[Secure Grader]
    H --> I[Protected Score]
    E --> J[Compare Band Inflation Delta]
    I --> J
    J --> K[Replay Scenario Telemetry]
```

---

## 3. Benchmark & Evidence Pipeline

```mermaid
flowchart TD
    A[Raw Sources] --> B[Source Registry]
    B --> C[License Tracking]
    C --> D[Canonical Schema]
    D --> E[Deduplication]
    E --> F[Quality Filter]
    F --> G[Attack Transformation]
    G --> H[Group-aware Split]
    H --> I[Benchmark Runner]
    I --> J[Performance Metrics]
    I --> K[Failure Analysis Engine]
    I --> L[Cryptographic Evidence Report]
```

---

## 4. Data Lineage Flow

```mermaid
flowchart LR
    S1[HF Benchmarks] --> R[Source Registry]
    S2[Kaggle Datasets] --> R
    S3[IELTS Essays] --> R
    S4[Hard Negatives] --> R
    R --> L[License Registry]
    L --> C[Canonical Schema]
    C --> D[Deduplication]
    D --> Q[Quality Filter]
    Q --> T[Attack Transformation]
    T --> G[Group-Aware Split]
    G --> H[Dataset SHA256 Hash]
    H --> E[Evidence Report]
```

---

## 5. Product Page Navigation Map

```mermaid
flowchart TD
    App[GradingGuard AI Platform] --> P1[/judge-view - Executive Summary]
    App --> P2[/playground - Security Sandbox]
    App --> P3[/attack-arena - Red-Team Arena]
    App --> P4[/benchmark - Robustness Suite]
    App --> P5[/data-lineage - Provenance Center]
    App --> P6[/evidence - Audit Viewer]
```
