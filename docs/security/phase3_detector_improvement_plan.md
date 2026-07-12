# Phase 3 Detector Improvement Plan

Status: pre-registered before detector changes

## Primary objective

Reduce generic false negatives and under-blocking on frozen paired evaluation without an uncontrolled false-positive regression.

Completion criteria:

- Frozen dataset hash remains `a89eb6c09be417209af94f7026e319840195c4239202bec9639242b6a5511549`.
- Frozen split hash remains `51e795858ff2d8460a4eeda9861407853a22bfbe6257dd9fd6bd3da983ef3fce`.
- Generic recall and under-block count improve on identical sample IDs.
- False-positive increase remains within accepted trade-off: generic false-positive rate must stay at or below 0.08.
- IELTS metrics retain LOW_SUPPORT label.
- No detector rule may embed benchmark sample IDs or suspicious long exact sample phrases.

## Targeted failure categories

- `false_negative`
- `under_block`
- `language_gap`
- `obfuscation_miss`
- `semantic_miss`
- `long_context_miss`
- `policy_routing_error`

## Development slices used

- `train` split aggregate failure patterns.
- Public test aggregate metrics.
- Synthetic unit fixtures not inserted into private holdout.

Private holdout policy:

- Do not inspect private-holdout sample content during tuning.
- Do not create exact-match rules from holdout text.
- Final holdout evaluation is run only after detector/config freeze.

## Intended detector changes

- Harden adversarial normalization for Unicode, bidirectional controls, URL-encoded text, and bounded Base64 evidence.
- Add general rule families for rubric override, prompt extraction, exfiltration, policy bypass, delimiter abuse, Vietnamese/mixed-language manipulation, and long suffix/prefix attacks.
- Add detector contribution objects with stable IDs, technique IDs, scores, confidence, evidence spans, and safe explanation keys.
- Add deterministic ensemble aggregation that treats unavailable detectors as unavailable, not as clean votes.
- Add static risk calibration and mode-aware policy routing for all six actions.

## Expected trade-offs

- Recall should improve.
- False positives may rise on security-discussion hard negatives; accepted only if explicit hard-negative tests pass and generic FPR remains within threshold.
- Local latency may increase slightly because normalization decodes bounded encodings.

## Embedding runtime decision

No large model download is authorized. Embedding remains optional. Phase 3 implements truthful health states and fallback-aware contribution handling; unavailable embedding must not count as a clean vote.

## Statistical comparison

Use paired before/after sample IDs:

- absolute count delta;
- rate delta;
- changed prediction categories;
- per-track support counts;
- McNemar-style discordant-pair counts where applicable.

No fabricated TOP 1 target is used.

