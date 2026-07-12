# IELTS Domain Security Data Card

Machine-readable samples: `datasets/canonical/phase2_canonical_security_samples.jsonl`

## Composition

- Track: `ielts_domain_security`
- Samples: 27
- Source: `internal_synthetic_ielts_security_v1`
- License status: INTERNAL_SYNTHETIC
- Domains: IELTS Writing Task 1, Writing Task 2, Reading, Speaking
- Languages: English, Vietnamese, mixed Vietnamese-English

## Attack-family coverage

Covered families include:

- direct score manipulation;
- indirect prompt injection;
- role spoofing;
- system prompt extraction;
- delimiter abuse;
- Unicode obfuscation;
- encoded payload;
- Vietnamese attack;
- mixed Vietnamese-English attack;
- long-context injection;
- data exfiltration;
- policy manipulation;
- instruction hidden in essay;
- instruction hidden in quoted/reference text.

## Hard-negative coverage

Covered clean categories include:

- normal IELTS essay;
- weak/strong writing with no attack;
- legitimate Band 9 discussion;
- academic prompt-injection discussion;
- quoted malicious phrase as analysis;
- code/technical passage;
- cybersecurity Reading content;
- legitimate feedback request;
- long clean context;
- multilingual clean content;
- punctuation/Unicode oddities;
- harmless imperatives.

## Split and review

Samples use deterministic group-hash splits and `single_reviewed` fixture annotation. Private holdout does not contain unresolved duplicate/leakage findings.

## Intended use

This track is a license-safe domain-security benchmark foundation. It is intentionally small and must carry LOW_SUPPORT warnings.

## Prohibited use

- Do not present this as an official IELTS scoring dataset.
- Do not commit unauthorized full IELTS passages.
- Do not tune detector thresholds in Phase 2.

