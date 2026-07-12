import re
from app.firewall.schemas import SanitizerResult


SUSPICIOUS_SPAN_PATTERNS = [
    re.compile(r"ignore\s+(?:previous|all|prior)?\s*instructions?[^\.\n]*", re.I),
    re.compile(r"disregard\s+(?:previous|all|prior)?\s*instructions?[^\.\n]*", re.I),
    re.compile(r"bỏ\s+qua\s+(?:các\s+)?hướng\s+dẫn[^\.\n]*", re.I),
    re.compile(r"(?:hãy\s+)?cho\s+bài\s+này\s+band\s+\d+(\.\d+)?[^\.\n]*", re.I),
    re.compile(r"give\s+(?:this\s+essay\s+|me\s+|this\s+answer\s+)?band\s+\d+(\.\d+)?[^\.\n]*", re.I),
    re.compile(r"(?:system|developer|assistant):\s*[^\.\n]*", re.I),
    re.compile(r"(?:show|print|reveal)\s+(?:the\s+)?(?:system|developer|scoring)?\s*prompt[^\.\n]*", re.I),
    re.compile(r"(?:disable|bypass|turn\s+off)\s+(?:the\s+)?(?:firewall|filter|policy)[^\.\n]*", re.I),
]
REPLACEMENT = "[Removed suspicious instruction targeting the AI grader]"
MAX_TRANSFORMATIONS = 20


def _merge_spans(spans: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not spans:
        return []
    merged = [spans[0]]
    for start, end in spans[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def sanitize_text(text: str) -> SanitizerResult:
    spans: list[tuple[int, int]] = []
    for pattern in SUSPICIOUS_SPAN_PATTERNS:
        for match in pattern.finditer(text):
            spans.append((match.start(), match.end()))

    spans = _merge_spans(sorted(set(spans)))[:MAX_TRANSFORMATIONS]
    if not spans:
        return SanitizerResult(
            cleaned_text=text,
            removed_spans=[],
            transformation_summary={"applied": False, "removed_span_count": 0},
        )

    removed_spans = [text[start:end] for start, end in spans]
    # Reject ambiguous transformations that would wipe the whole submission.
    removed_chars = sum(end - start for start, end in spans)
    if removed_chars >= max(len(text.strip()) * 0.85, 1):
        return SanitizerResult(
            cleaned_text=text,
            removed_spans=[],
            transformation_summary={
                "applied": False,
                "rejected_reason": "would_remove_most_content",
                "candidate_span_count": len(spans),
            },
        )

    parts: list[str] = []
    cursor = 0
    for start, end in spans:
        parts.append(text[cursor:start])
        parts.append(REPLACEMENT)
        cursor = end
    parts.append(text[cursor:])
    cleaned_text = "".join(parts)

    return SanitizerResult(
        cleaned_text=cleaned_text.strip(),
        removed_spans=removed_spans,
        transformation_summary={
            "applied": True,
            "removed_span_count": len(removed_spans),
            "max_transformations": MAX_TRANSFORMATIONS,
            "replacement": "stable_public_placeholder",
        },
    )
