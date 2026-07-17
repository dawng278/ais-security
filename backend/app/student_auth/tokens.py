from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from app.config import settings


@dataclass(frozen=True)
class StudentTokenPayload:
    student_id: str
    email: str
    session_id: str


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(message: str, secret: str) -> str:
    return _b64url_encode(hmac.new(secret.encode("utf-8"), message.encode("ascii"), hashlib.sha256).digest())


def create_student_access_token(student_id: str, email: str, session_id: str, ttl_seconds: int | None = None) -> str:
    ttl = settings.student_access_token_ttl_seconds if ttl_seconds is None else ttl_seconds
    now = int(time.time())
    header = {"alg": "HS256", "typ": "GGSTU"}
    payload = {
        "sub": student_id,
        "email": email,
        "sid": session_id,
        "iat": now,
        "exp": now + ttl,
    }
    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{header_b64}.{payload_b64}"
    signature = _sign(message, settings.student_token_secret)
    return f"{message}.{signature}"


def verify_student_access_token(token: str) -> StudentTokenPayload:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("malformed_token")
    header_b64, payload_b64, signature = parts
    message = f"{header_b64}.{payload_b64}"
    expected_signature = _sign(message, settings.student_token_secret)
    if not hmac.compare_digest(signature, expected_signature):
        raise ValueError("invalid_signature")
    try:
        payload = json.loads(_b64url_decode(payload_b64))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError("malformed_payload") from exc
    if payload.get("exp", 0) < int(time.time()):
        raise ValueError("token_expired")
    try:
        return StudentTokenPayload(student_id=payload["sub"], email=payload["email"], session_id=payload["sid"])
    except KeyError as exc:
        raise ValueError("malformed_payload") from exc
