from __future__ import annotations

import base64
import hashlib
import hmac
import json
from dataclasses import dataclass
from time import time
from typing import Iterable

from fastapi import Header

from app.config import settings
from app.operational.errors import GatewayException


ROLES = {"viewer", "analyst", "policy_manager", "security_admin", "integration_service"}

PERMISSIONS: dict[str, set[str]] = {
    "viewer": {"decisions:read", "evidence:read", "runtime:read"},
    "analyst": {"decisions:read", "incidents:read", "reviews:read", "reviews:write", "sensitive:read"},
    "policy_manager": {"policies:read", "policies:write", "policies:validate"},
    "security_admin": {
        "decisions:read",
        "incidents:read",
        "reviews:read",
        "reviews:write",
        "policies:read",
        "policies:write",
        "policies:publish",
        "runtime:read",
        "runtime:write",
        "clients:write",
        "audit:read",
        "sensitive:read",
    },
    "integration_service": {"gateway:submit", "decisions:own_read", "runtime:read"},
}


@dataclass(frozen=True)
class Actor:
    subject: str
    actor_type: str
    roles: tuple[str, ...]
    client_id: str
    tenant: str
    issued_at: int
    expires_at: int

    @property
    def permissions(self) -> set[str]:
        merged: set[str] = set()
        for role in self.roles:
            merged |= PERMISSIONS.get(role, set())
        return merged

    def require(self, permission: str) -> None:
        if permission not in self.permissions:
            raise GatewayException("FORBIDDEN", detail=f"missing_permission:{permission}")


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _sign(message: str, secret: str) -> str:
    return _b64url_encode(hmac.new(secret.encode("utf-8"), message.encode("ascii"), hashlib.sha256).digest())


def create_signed_token(
    *,
    subject: str,
    roles: Iterable[str],
    client_id: str = "local-client",
    tenant: str = "local",
    actor_type: str = "integration_client",
    ttl_seconds: int = 3600,
    secret: str | None = None,
) -> str:
    now = int(time())
    payload = {
        "iss": settings.auth_issuer,
        "aud": settings.auth_audience,
        "sub": subject,
        "roles": list(roles),
        "client_id": client_id,
        "tenant": tenant,
        "actor_type": actor_type,
        "iat": now,
        "exp": now + ttl_seconds,
    }
    header = {"alg": "HS256", "typ": "GGJWT"}
    head = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    body = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    message = f"{head}.{body}"
    return f"{message}.{_sign(message, secret or settings.auth_token_secret)}"


def verify_signed_token(token: str) -> Actor:
    parts = token.split(".")
    if len(parts) != 3:
        raise GatewayException("UNAUTHORIZED", detail="malformed_token")
    message = f"{parts[0]}.{parts[1]}"
    expected = _sign(message, settings.auth_token_secret)
    if not hmac.compare_digest(parts[2], expected):
        raise GatewayException("UNAUTHORIZED", detail="invalid_signature")
    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
    except Exception as exc:  # noqa: BLE001 - deliberately normalize auth parsing failures.
        raise GatewayException("UNAUTHORIZED", detail="invalid_token_encoding") from exc
    if header.get("alg") != "HS256":
        raise GatewayException("UNAUTHORIZED", detail="unsupported_alg")
    now = int(time())
    if payload.get("iss") != settings.auth_issuer or payload.get("aud") != settings.auth_audience:
        raise GatewayException("UNAUTHORIZED", detail="issuer_or_audience_mismatch")
    if int(payload.get("exp", 0)) <= now:
        raise GatewayException("UNAUTHORIZED", detail="expired_token")
    roles = tuple(role for role in payload.get("roles", []) if role in ROLES)
    if not roles:
        raise GatewayException("FORBIDDEN", detail="no_valid_roles")
    return Actor(
        subject=str(payload["sub"]),
        actor_type=str(payload.get("actor_type", "user")),
        roles=roles,
        client_id=str(payload.get("client_id", "")),
        tenant=str(payload.get("tenant", "default")),
        issued_at=int(payload.get("iat", 0)),
        expires_at=int(payload["exp"]),
    )


def require_actor(authorization: str | None = Header(default=None)) -> Actor:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise GatewayException("UNAUTHORIZED", detail="missing_bearer_token")
    token = authorization.split(" ", 1)[1].strip()
    return verify_signed_token(token)


def require_permission(actor: Actor, permission: str) -> Actor:
    actor.require(permission)
    return actor

