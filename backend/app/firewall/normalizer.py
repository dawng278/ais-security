import base64
import binascii
import html
import re
import unicodedata
from dataclasses import dataclass


ZERO_WIDTH_RE = re.compile(r"[\u200B-\u200D\uFEFF]")
BIDI_CONTROL_RE = re.compile(r"[\u202A-\u202E\u2066-\u2069]")
CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
BASE64_LIKE_RE = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{24,}={0,2}(?![A-Za-z0-9+/=])")
URL_ENCODED_RE = re.compile(r"(?:%[0-9A-Fa-f]{2}){3,}")
CODE_BLOCK_RE = re.compile(r"```|~~~|<script|</script", re.IGNORECASE)
MAX_DECODED_CHARS = 2000
MAX_NESTED_DECODE_DEPTH = 2


@dataclass
class NormalizationResult:
    normalized_text: str
    flags: list[str]
    transformations: list[dict] | None = None


def decode_base64_text(value: str) -> str | None:
    if len(value) < 24:
        return None
    try:
        decoded = base64.b64decode(value, validate=True)
        if len(decoded) > MAX_DECODED_CHARS:
            return None
        text = decoded.decode("utf-8")
        if not text.strip():
            return None
        # Reject mostly binary/control payloads. We only need safe text evidence.
        printable = sum(1 for ch in text if ch.isprintable() or ch.isspace())
        if printable / max(len(text), 1) < 0.85:
            return None
        return text
    except (binascii.Error, ValueError):
        return None
    except UnicodeDecodeError:
        return None


def looks_like_base64(value: str) -> bool:
    return decode_base64_text(value) is not None


def decode_url_limited(value: str) -> str | None:
    from urllib.parse import unquote

    if len(value) > MAX_DECODED_CHARS:
        return None
    decoded = unquote(value)
    if decoded == value or len(decoded) > MAX_DECODED_CHARS:
        return None
    return decoded


def normalize_text(text: str) -> NormalizationResult:
    flags: list[str] = []
    transformations: list[dict] = []

    original = text

    text = unicodedata.normalize("NFKC", text)
    if text != original:
        flags.append("unicode_nfkc_applied")
        transformations.append({"type": "unicode_nfkc_applied"})

    if ZERO_WIDTH_RE.search(text):
        flags.append("zero_width_removed")
        text = ZERO_WIDTH_RE.sub("", text)
        transformations.append({"type": "zero_width_removed"})

    if BIDI_CONTROL_RE.search(text):
        flags.append("bidi_control_removed")
        text = BIDI_CONTROL_RE.sub("", text)
        transformations.append({"type": "bidi_control_removed"})

    if CONTROL_CHAR_RE.search(text):
        flags.append("control_char_removed")
        text = CONTROL_CHAR_RE.sub(" ", text)
        transformations.append({"type": "control_char_removed"})

    decoded = html.unescape(text)
    if decoded != text:
        flags.append("html_entities_decoded")
        text = decoded
        transformations.append({"type": "html_entities_decoded"})

    if CODE_BLOCK_RE.search(text):
        flags.append("markdown_or_code_block_detected")

    decoded_evidence: list[str] = []
    for match in URL_ENCODED_RE.findall(text):
        decoded_url = decode_url_limited(match)
        if decoded_url:
            flags.append("url_encoded_payload_detected")
            transformations.append({"type": "url_decoded_evidence", "decoded_length": len(decoded_url)})
            decoded_evidence.append(decoded_url)
            break

    for match in BASE64_LIKE_RE.findall(text):
        decoded_b64 = decode_base64_text(match)
        if decoded_b64:
            flags.append("base64_like_payload_detected")
            transformations.append({"type": "base64_decoded_evidence", "decoded_length": len(decoded_b64)})
            decoded_evidence.append(decoded_b64)
            break

    # Add bounded decoded text to analysis input so detectors can inspect it.
    # Original input is preserved by caller; decoded content is never executed.
    if decoded_evidence:
        text = text + " " + " ".join(decoded_evidence[:MAX_NESTED_DECODE_DEPTH])

    lowered = text.lower()
    normalized = re.sub(r"\s+", " ", lowered).strip()

    return NormalizationResult(
        normalized_text=normalized,
        flags=flags,
        transformations=transformations,
    )
