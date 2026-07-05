# Threat Model: GradingGuard AI

> **Security Risk Assessment, Attacker Personas, and Defense Control Matrix**

---

## 1. System Context

GradingGuard AI acts as an inline security gateway protecting LLM-based automated essay scoring engines. Student submissions originate from external untrusted client devices, pass through the GradingGuard AI firewall, and are delivered to the downstream grading model.

---

## 2. Protected Assets

1. **IELTS Band Score Validity**: Ensuring reported band scores accurately reflect candidate language ability.
2. **Grading Rubric Integrity**: Enforcing Task Achievement, Coherence, Lexical, and Grammar boundary constraints.
3. **System Prompt Boundaries**: Preventing unauthorized instructions from hijacking LLM execution context.
4. **Audit & Evidence Trail**: Protecting historical evaluation reports and SHA256 hashes against tampering.
5. **Platform Trust & Institutional Credibility**: Safeguarding assessment authority reputation.

---

## 3. Trust Boundaries

- **Boundary 1 (Client → Gateway)**: Untrusted student input entering the system API.
- **Boundary 2 (Gateway → Grader)**: Sanitized text passing to the internal LLM context window.
- **Boundary 3 (Grader → Audit Log)**: Verified evaluation outputs stored in persistent evidence storage.

---

## 4. Attacker Profiles

- **Novice Cheater**: Uses copy-pasted English override instructions.
- **Multilingual Attacker**: Translates malicious instructions into non-English languages (Vietnamese, Chinese).
- **Obfuscation Attacker**: Employs Base64, hex encoding, or invisible Unicode characters.
- **Adaptive Attacker**: Implements complex role spoofing, fake system tags, and indirect delimiter injections.

---

## 5. Attack Vectors

- **Direct Score Manipulation**: Exploit system prompt weakness to command a specific band score.
- **Multilingual Payload Injection**: Evasion of English-only keyword filters.
- **Role Spoofing**: Injecting markdown headers such as `[SYSTEM UPDATE]` or `<<<ADMIN>>>`.
- **Unicode Obfuscation**: Hiding payload text using zero-width spaces or homoglyph substitution.
- **Indirect Delimiter Exploitation**: Using custom XML/Markdown closing tags to break out of student essay prompt boundaries.

---

## 6. Security Controls

- **Input Normalization**: NFKC Unicode standardization and zero-width character stripping.
- **Multi-Pattern & Semantic Detector**: Combined regex heuristics, role-spoofing classifiers, and embedding distance vectors.
- **Risk Scoring & Routing Engine**: Action allocation (`allow`, `warn`, `secure_grade`, `manual_review`).
- **Span-Level Sanitizer**: Target extraction and removal of malicious instruction spans.
- **Delimiter-Isolated System Prompts**: Strict tag isolation during downstream LLM execution.
- **Score Integrity Verifier**: Automated delta comparison between baseline and secure scores.

---

## 7. Risk Matrix

| Threat | Likelihood | Impact | Risk | Control Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Direct score manipulation** | High | High | **Critical** | Multi-pattern detector + span sanitizer + secure grader |
| **Multilingual injection** | High | High | **Critical** | Multilingual pattern dictionary + semantic distance signals |
| **Role spoofing** | Medium | High | **High** | Role spoofing classifier + system prompt boundary isolation |
| **Unicode obfuscation** | Medium | Medium | **Medium** | Input normalizer + zero-width stripper + obfuscation detector |
| **Benign cybersecurity essay false positive** | Medium | Medium | **Medium** | Hard-negative dataset tuning + failure analysis engine |
| **Score instability after sanitization** | Medium | High | **High** | Score Integrity Verifier + clean utility loss tracking |

---

## 8. Residual Risks

- **Novel Obfuscation Mutants**: Highly novel obfuscations may bypass heuristic pattern matching if embedding transformer packages are unavailable.
- **Manual Review Backlog**: High-risk ambiguous submissions ($R \ge 0.85$) increase human examiner queue length.

---

## 9. Mitigation Roadmap

1. Deploy hardware-accelerated ONNX semantic embedding detector to eliminate heuristic fallback dependence.
2. Automate active learning pipeline to retrain detector rules on newly discovered failure logs.
3. Extend threat modeling and firewall controls to multimodal IELTS Speaking audio streams.
