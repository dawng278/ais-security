# Sanitization Contract

Phase 3 sanitizer behavior:

- operates on bounded suspicious spans;
- preserves legitimate essay content;
- preserves original input outside sanitizer result;
- generates sanitized output and transformation summary;
- merges overlapping spans;
- rejects transformations that would remove most of the submission;
- is idempotent for already-sanitized output;
- uses a stable public placeholder.

Sanitization must not:

- change the IELTS score itself;
- inject replacement instructions;
- reveal internal detection logic;
- mutate source input in-place;
- turn clean essays into malformed text.

