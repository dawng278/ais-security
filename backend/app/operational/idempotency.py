from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from app.operational.database import SecurityStore
from app.operational.errors import GatewayException
from app.operational.time import utc_now, utc_now_iso


def fingerprint_payload(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_idempotency_key(key: str | None) -> str | None:
    if key is None or key == "":
        return None
    if not 8 <= len(key) <= 128 or any(ch.isspace() for ch in key):
        raise GatewayException("INVALID_REQUEST", detail="invalid_idempotency_key")
    return key


def scoped_key(actor_scope: str, route: str, key: str) -> str:
    return f"{actor_scope}:{route}:{key}"


def begin_idempotent_request(
    store: SecurityStore,
    *,
    actor_scope: str,
    route: str,
    key: str | None,
    request_payload: Any,
) -> tuple[str | None, dict[str, Any] | None]:
    key = validate_idempotency_key(key)
    if key is None:
        return None, None
    scope_key = scoped_key(actor_scope, route, key)
    fp = fingerprint_payload(request_payload)
    existing = store.fetch_one("SELECT * FROM idempotency_records WHERE scoped_key = ?", (scope_key,))
    if existing:
        if existing["request_fingerprint"] != fp:
            raise GatewayException("CONFLICT", detail="idempotency_key_payload_mismatch")
        if existing["status"] == "completed" and existing["response_json"]:
            return scope_key, json.loads(existing["response_json"])
        raise GatewayException("CONFLICT", detail="idempotency_request_in_progress")
    expires = (utc_now() + timedelta(hours=24)).astimezone(UTC).isoformat().replace("+00:00", "Z")
    store.execute(
        """
        INSERT INTO idempotency_records(scoped_key, actor_scope, request_fingerprint, status, response_json, target_id, expires_at, created_at, updated_at)
        VALUES (?, ?, ?, 'pending', NULL, NULL, ?, ?, ?)
        """,
        (scope_key, actor_scope, fp, expires, utc_now_iso(), utc_now_iso()),
    )
    return scope_key, None


def complete_idempotent_request(
    store: SecurityStore,
    *,
    scope_key: str | None,
    response_payload: dict[str, Any],
    target_id: str | None = None,
) -> None:
    if scope_key is None:
        return
    store.execute(
        """
        UPDATE idempotency_records
        SET status = 'completed', response_json = ?, target_id = ?, updated_at = ?
        WHERE scoped_key = ?
        """,
        (json.dumps(response_payload, sort_keys=True), target_id, utc_now_iso(), scope_key),
    )

