from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d .()-]{7,}\d)(?!\d)")
BEARER_RE = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{12,}")
API_KEY_RE = re.compile(r"(?i)\b(?:api[_-]?key|secret|token)\s*[:=]\s*[A-Za-z0-9._~+/=-]{8,}")
LONG_SECRET_RE = re.compile(r"\b[A-Za-z0-9_\-]{32,}\b")


@dataclass(frozen=True)
class RedactionResult:
    redacted_text: str
    preview: str
    content_hash: str
    redaction_state: str
    redacted_counts: dict[str, int]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def redact_text(text: str, *, max_preview: int = 240) -> RedactionResult:
    counts: dict[str, int] = {}
    redacted = text
    for name, pattern, replacement in [
        ("email", EMAIL_RE, "[REDACTED_EMAIL]"),
        ("phone", PHONE_RE, "[REDACTED_PHONE]"),
        ("bearer_token", BEARER_RE, "[REDACTED_BEARER_TOKEN]"),
        ("api_key", API_KEY_RE, "[REDACTED_SECRET]"),
        ("secret_like", LONG_SECRET_RE, "[REDACTED_SECRET_LIKE]"),
    ]:
        redacted, count = pattern.subn(replacement, redacted)
        if count:
            counts[name] = count
    preview = redacted.replace("\r", " ").replace("\n", " ")
    if len(preview) > max_preview:
        preview = preview[: max_preview - 1] + "…"
    return RedactionResult(
        redacted_text=redacted,
        preview=preview,
        content_hash=sha256_text(text),
        redaction_state="redacted" if counts else "none_detected",
        redacted_counts=counts,
    )

