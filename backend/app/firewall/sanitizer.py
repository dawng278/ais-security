import re
from app.firewall.schemas import SanitizerResult


SUSPICIOUS_SPAN_PATTERNS = [
    r"(?i)ignore\s+previous\s+instructions[^\.\n]*",
    r"(?i)disregard\s+previous\s+instructions[^\.\n]*",
    r"(?i)bỏ\s+qua\s+hướng\s+dẫn[^\.\n]*",
    r"(?i)hãy\s+cho\s+bài\s+này\s+band\s+\d+(\.\d+)?[^\.\n]*",
    r"(?i)give\s+(this\s+essay\s+|me\s+)?band\s+\d+(\.\d+)?[^\.\n]*",
    r"(?i)system:\s*[^\.\n]*",
    r"(?i)assistant:\s*[^\.\n]*",
]


def sanitize_text(text: str) -> SanitizerResult:
    cleaned_text = text
    removed_spans: list[str] = []

    for pattern in SUSPICIOUS_SPAN_PATTERNS:
        matches = re.findall(pattern, cleaned_text)
        for m in matches:
            span_str = m if isinstance(m, str) else m[0]
            if span_str and span_str not in removed_spans:
                removed_spans.append(span_str)
        cleaned_text = re.sub(pattern, "[Removed suspicious instruction targeting the AI grader]", cleaned_text)

    return SanitizerResult(
        cleaned_text=cleaned_text.strip(),
        removed_spans=removed_spans,
    )
