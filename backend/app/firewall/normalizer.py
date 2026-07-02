import base64
import binascii
import html
import re
import unicodedata
from dataclasses import dataclass


ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF]")
BASE64_LIKE_RE = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}\b")
CODE_BLOCK_RE = re.compile(r"```|~~~|<script|</script", re.IGNORECASE)


@dataclass
class NormalizationResult:
    normalized_text: str
    flags: list[str]


def looks_like_base64(value: str) -> bool:
    if len(value) < 24:
        return False
    try:
        base64.b64decode(value, validate=True)
        return True
    except (binascii.Error, ValueError):
        return False


def normalize_text(text: str) -> NormalizationResult:
    flags: list[str] = []

    original = text

    text = unicodedata.normalize("NFKC", text)
    if text != original:
        flags.append("unicode_nfkc_applied")

    if ZERO_WIDTH_RE.search(text):
        flags.append("zero_width_removed")
        text = ZERO_WIDTH_RE.sub("", text)

    decoded = html.unescape(text)
    if decoded != text:
        flags.append("html_entities_decoded")
        text = decoded

    if CODE_BLOCK_RE.search(text):
        flags.append("markdown_or_code_block_detected")

    for match in BASE64_LIKE_RE.findall(text):
        if looks_like_base64(match):
            flags.append("base64_like_payload_detected")
            break

    lowered = text.lower()
    normalized = re.sub(r"\s+", " ", lowered).strip()

    return NormalizationResult(
        normalized_text=normalized,
        flags=flags,
    )
