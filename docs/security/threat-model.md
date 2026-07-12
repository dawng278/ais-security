# Threat Model

Status: Phase 1 contract  
Method: STRIDE-inspired abuse-case inventory for a grading security gateway

## Assets

- Candidate submission content.
- Grader system instructions.
- Grading rubric.
- Model credentials.
- Policy configuration.
- Detector models and detector runtime state.
- Decision evidence.
- Audit records.
- Reviewer actions.
- Grading outcome.
- Benchmark integrity.

## Threat actors

- Malicious candidate.
- Curious candidate.
- Compromised integration client.
- Malicious insider.
- External attacker.
- Poisoned data source.
- Compromised dependency.
- Accidental administrator.
- Faulty model/provider.

## Entry points

- Submission API.
- Grader adapter.
- Policy API.
- Analyst console.
- Benchmark ingestion.
- Dataset ingestion.
- Evidence export.
- Logs.
- Configuration.
- Model loading.

## Trust boundaries

- Candidate -> GAU IELTS.
- GAU IELTS -> GradingGuard.
- GradingGuard -> detector runtime.
- GradingGuard -> grader.
- GradingGuard -> audit storage.
- Analyst console -> backend.
- Benchmark environment -> evidence artifacts.
- External datasets -> canonical dataset.

## Abuse cases

Each row includes attacker goal, preconditions, path, affected assets, controls, residual risk, required tests, and operating-mode impact.

| threat | goal | preconditions | path | affected assets | current controls | proposed controls | residual risk | required tests | operating-mode impact |
|---|---|---|---|---|---|---|---|---|---|
| `direct_prompt_injection` | Override grading instructions. | Candidate can submit text. | Plain-language instruction inside answer. | grader instructions, score. | heuristics, risk engine. | policy action contract, secure grader isolation. | novel phrasing. | positive + hard-negative injection tests. | shadow audits only; warn attaches warning; enforce applies policy. |
| `indirect_prompt_injection` | Hide instructions in quoted/external content. | Prompt accepts pasted content. | Citation, quote, or embedded task text. | grader instructions, evidence. | partial heuristics. | context-aware spans, review escalation. | ambiguous legitimate quotes. | quote vs attack tests. | warn/degraded should avoid silent score modification. |
| `role_spoofing` | Pretend to be system/developer/examiner. | Candidate can include role labels. | Markdown role blocks or authority claims. | grader instructions. | category rules. | delimiter-aware parsing, policy priority. | mixed legitimate examples. | role marker hard negatives. | enforce may manual_review or block by policy. |
| `score_manipulation` | Inflate band score. | Grader follows candidate text too strongly. | “Give band 9” or rubric override. | grading outcome. | mock verifier, heuristics. | score-integrity track, protected grader adapter. | subtle self-praise. | score drift and recovery tests. | enforce can secure_grade/manual_review. |
| `system_prompt_extraction` | Reveal hidden grader prompt. | Model can answer meta-instructions. | Ask grader to print prompt/rubric secrets. | system prompt, rubric. | heuristics. | adapter refusal validation, output filters. | provider-specific leakage. | extraction prompt tests. | enforce should block or secure_grade without raw leakage. |
| `data_exfiltration` | Extract other candidate/audit data. | Backend has stored sensitive data. | Prompt requests logs, prior submissions, secrets. | candidate content, audit. | no persistent store currently. | least-privilege adapter, redaction, RBAC. | insider access. | exfil prompt and permission tests. | degraded must not reveal raw evidence. |
| `delimiter_abuse` | Break system/user boundaries. | Grader prompt uses delimiters. | XML/Markdown/code-fence escape. | grader instructions. | heuristic categories. | structured adapter channels, delimiter tests. | novel delimiters. | delimiter escape tests. | enforce may manual_review. |
| `unicode_obfuscation` | Evade rules. | Candidate can submit Unicode. | Homoglyphs, zero-width, bidi controls. | detector evidence. | normalizer, obfuscation detector. | canonical normalized evidence. | false positives in multilingual text. | Unicode positive/hard-negative tests. | warn can continue-with-warning. |
| `encoding_attack` | Hide instructions. | Candidate can submit encoded text. | Base64, hex, URL encoding. | detector evidence. | base64 heuristics. | bounded decoding detector with audit. | benign encoded examples. | encoded payload tests. | enforce can sanitize/review. |
| `long_context_attack` | Bury instructions. | Long content accepted. | Late-context override or repeated noise. | grader instructions, latency. | length limits in schema. | chunked detector, timeout budget. | missed distant spans. | long-context tests. | malformed/oversized rules apply. |
| `multilingual_attack` | Evade English-centric rules. | Non-English text accepted. | Vietnamese/Chinese/mixed-language override. | score, detector accuracy. | multilingual heuristics/prototypes. | language-aware benchmark track. | low-resource language gaps. | multilingual positive/hard-negative tests. | warn/degraded must label uncertainty. |
| `policy_manipulation` | Change enforcement behavior. | Policy API/config access. | Unauthorized edit or malicious rollback. | policy configuration. | none persistent currently. | policy lifecycle, RBAC, audit. | admin mistake. | policy permission/conflict tests. | enforce requires published policy and rollback. |
| `grader_output_manipulation` | Make grader return invalid/unsafe output. | Model/provider output not validated. | Prompt induces malformed JSON or inflated scores. | grading outcome. | mock grader only. | structured validation, score range checks. | provider drift. | invalid output tests. | enforce rejects/manual_review on invalid grader output. |
| `audit_tampering` | Hide evidence. | Access to logs/artifacts. | Edit/delete audit entries. | audit records. | evidence hashing. | append-oriented storage, correction events. | filesystem compromise. | tamper detection tests. | audit unavailable matrix applies. |
| `evidence_tampering` | Fake benchmark/evidence results. | Write access to artifacts. | Modify report JSON/MD. | benchmark integrity. | Phase 0 checksum discipline. | signed/checksummed exports. | local repo compromise. | checksum and claim-drift tests. | competition gate blocks unsupported claims. |
| `replay` | Reuse old request/decision. | Attacker has request payload. | Replay request_id/correlation_id. | audit, quota, score. | no persistent dedupe currently. | idempotency and nonce store. | clock skew. | replay tests. | enforce rejects conflict. |
| `duplicate_submission` | Inflate workload or evade review. | Repeat similar submissions. | Minor edits or duplicate IDs. | audit, reviewer queue. | none persistent currently. | similarity/dedupe in pilot. | legitimate retries. | duplicate tests. | warn/enforce queue dedupe. |
| `privilege_escalation` | Access admin/reviewer actions. | Console/API auth missing. | Call protected routes or forge roles. | policy, review, raw content. | not implemented. | auth/RBAC phase, audit sensitive access. | misconfigured roles. | RBAC tests later. | pilot/prod blocked until implemented. |
| `sensitive_data_leakage` | Expose PII/secrets. | Logs or UI show raw content. | Evidence export, stack trace, raw logs. | candidate IDs, essays, keys. | claim/audit discipline. | redaction/retention contract. | over-broad exports. | redaction tests. | degraded/error paths must stay redacted. |
| `dependency_failure` | Cause unsafe fallback. | Dependency unavailable. | Missing model/package/provider. | detector, grader. | embedding health evidence. | health-state contract and failure matrix. | partial silent degradation. | dependency injection tests. | degraded mode reason required. |
| `detector_outage` | Bypass detection. | Detectors unavailable/disabled. | Runtime failure. | score, evidence. | rule detector present, embedding fallback. | fail-mode matrix, health gating. | all detectors down. | detector outage tests. | enforce may fail-closed/manual_review. |
| `grader_outage` | Deny service or force bypass. | Provider unavailable. | Timeout/network error. | availability, score. | mock only. | adapter retry/timeout contract. | provider incident. | timeout/retry tests. | reject/retry/manual_review by mode. |
| `policy_store_outage` | Use stale/unknown policy. | Policy persistence unavailable. | Store read failure. | action semantics. | no store currently. | cached published policy + rollback contract. | stale policy. | policy outage tests. | enforce fail-closed/manual_review. |
| `audit_store_outage` | Hide decisions. | Audit persistence unavailable. | Storage write failure. | audit records. | no persistent store currently. | append-oriented store and degraded mode. | lost audit during outage. | audit write failure tests. | enforce should not silently continue. |

## Residual critical decisions

No critical architecture decision remains unresolved for Phase 1. Implementation details for RBAC, persistence, detector tuning, and real grader integration are intentionally deferred to later phases.

