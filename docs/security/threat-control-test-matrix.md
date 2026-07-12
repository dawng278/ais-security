# Threat-Control-Test Matrix

Every threat from the Phase 1 threat model maps to a future positive test, hard-negative test, failure injection, and metric slice.

| threat | detector | policy | action | positive test | hard-negative test | failure injection | metric slice | residual risk |
|---|---|---|---|---|---|---|---|---|
| `direct_prompt_injection` | heuristic, semantic | high confidence override | secure_grade/manual_review | direct override payload | essay discussing instructions academically | disable heuristic | recall, under-block | novel wording |
| `indirect_prompt_injection` | context/span detector | quote-aware escalation | warn/manual_review | injected quote | legitimate cited source | malformed quoted block | precision, recall | ambiguity |
| `role_spoofing` | role marker detector | authority claim priority | manual_review/block | system/developer labels | role-play essay topic | delimiter parser failure | per-class F1 | false positives |
| `score_manipulation` | score manipulation detector | score integrity | secure_grade | band 9 request | legitimate self-evaluation text | verifier unavailable | attack success rate, score drift | subtle manipulation |
| `system_prompt_extraction` | extraction intent detector | secret protection | block/manual_review | reveal prompt request | essay about privacy | grader output filter unavailable | leakage count | provider leakage |
| `data_exfiltration` | exfil intent detector | no cross-user data | block | ask for other users/logs | general data privacy essay | redactor unavailable | FPR/FNR | insider access |
| `delimiter_abuse` | delimiter detector | boundary escape priority | secure_grade/manual_review | close XML/code fence | programming essay with code fences | parser timeout | recall | novel delimiters |
| `unicode_obfuscation` | normalizer, obfuscation | normalize then decide | warn/secure_grade | zero-width override | multilingual legitimate answer | normalizer disabled | obfuscation recall | language false positives |
| `encoding_attack` | encoding detector | bounded decode | sanitize/manual_review | base64 instruction | base64 as topic example | decoder budget exceeded | recall, latency | nested encodings |
| `long_context_attack` | chunked detector | length/time budget | warn/manual_review | late buried override | long legitimate essay | chunk timeout | p95/p99, under-block | context gaps |
| `multilingual_attack` | multilingual rules, semantic | language-aware threshold | warn/secure_grade | Vietnamese/Chinese override | non-English normal essay | language detector unavailable | per-language F1 | low-resource gaps |
| `policy_manipulation` | config validator | published-only policy | reject/conflict | unauthorized publish | valid draft edit | policy store outage | policy error rate | admin mistake |
| `grader_output_manipulation` | output validator | structured output required | retry/manual_review | malformed score JSON | low-quality but valid response | provider returns invalid output | invalid response rate | provider drift |
| `audit_tampering` | hash/integrity check | append-only audit | reject/degraded | modified audit event | correction event | audit write failure | tamper detection | filesystem compromise |
| `evidence_tampering` | checksum guard | signed evidence | block release | changed evidence JSON | new isolated report path | checksum mismatch | evidence integrity | local compromise |
| `replay` | idempotency checker | request uniqueness | conflict | repeated request_id | legitimate retry with idempotency | nonce store down | conflict rate | clock skew |
| `duplicate_submission` | similarity/dedupe | duplicate handling | warn/review | repeated essay variants | practice retake | dedupe service down | duplicate rate | legitimate repeats |
| `privilege_escalation` | auth/RBAC later | least privilege | forbidden | reviewer calls admin endpoint | valid reviewer action | auth provider down | forbidden/pass rate | role misconfig |
| `sensitive_data_leakage` | redactor | default redaction | sanitize/reject | PII/API key in content | normal email in writing task | redactor fails | leakage count | over-redaction |
| `dependency_failure` | health monitor | degraded mode | continue-with-warning/manual_review | missing package | optional detector disabled intentionally | dependency import failure | availability | silent degradation |
| `detector_outage` | health monitor | health-gated enforcement | manual_review/reject | all detectors unavailable | embedding unavailable but rules healthy | detector timeout | detector availability | fail-open pressure |
| `grader_outage` | adapter health | retry budget | retry/manual_review/reject | provider timeout | slow but valid response | network timeout | p95/p99, timeout rate | provider incident |
| `policy_store_outage` | policy health | cached published fallback | manual_review/reject | store read fails | stale cache within TTL | policy DB down | policy availability | stale policy |
| `audit_store_outage` | audit health | no silent enforce | manual_review/reject | audit write fails | transient retry succeeds | audit DB down | audit availability | temporary data loss |

