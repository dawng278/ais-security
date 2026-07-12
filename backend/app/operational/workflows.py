from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

from app.config import settings
from app.operational.auth import Actor
from app.operational.database import SecurityStore
from app.operational.errors import GatewayException
from app.operational.redaction import redact_text
from app.operational.schemas import AssignReviewRequest, ModeChangeRequest, PolicyDraftRequest, ResolveReviewRequest, StartReviewRequest
from app.operational.time import utc_now_iso


VALID_POLICY_ACTIONS = {"allow", "warn", "sanitize", "secure_grade", "manual_review", "block"}
VALID_MODES = {"shadow", "warn", "enforce", "degraded"}


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _checksum(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _validate_policy_document(policy: dict[str, Any]) -> None:
    if "action" not in policy or policy["action"] not in VALID_POLICY_ACTIONS:
        raise GatewayException("INVALID_REQUEST", detail="invalid_policy_action")
    modes = set(policy.get("operating_modes", ["shadow"]))
    if not modes or not modes <= VALID_MODES:
        raise GatewayException("INVALID_REQUEST", detail="invalid_policy_modes")
    if any(key in policy for key in {"python", "eval", "__import__", "exec"}):
        raise GatewayException("INVALID_REQUEST", detail="unsafe_policy_expression")


def create_policy_draft(store: SecurityStore, actor: Actor, request: PolicyDraftRequest) -> dict[str, Any]:
    actor.require("policies:write")
    _validate_policy_document(request.policy)
    now = utc_now_iso()
    version_id = f"polv_{uuid.uuid4()}"
    checksum = _checksum(request.policy)
    with store.connect() as con:
        con.execute(
            """
            INSERT OR IGNORE INTO security_policies(policy_id, name, active_version_id, created_at, updated_at)
            VALUES (?, ?, NULL, ?, ?)
            """,
            (request.policy_id, request.name, now, now),
        )
        con.execute(
            """
            INSERT INTO security_policy_versions(
              version_id, policy_id, version, status, policy_json, checksum, created_by, approved_by,
              created_at, updated_at, published_at
            ) VALUES (?, ?, ?, 'validated', ?, ?, ?, NULL, ?, ?, NULL)
            """,
            (version_id, request.policy_id, request.version, _json(request.policy), checksum, actor.subject, now, now),
        )
    store.audit(
        correlation_id=f"policy-{version_id}",
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="policy_validated",
        target_type="security_policy_version",
        target_id=version_id,
        environment=settings.env,
        policy_version=request.version,
        safe_metadata={"policy_id": request.policy_id, "checksum": checksum},
    )
    return {"version_id": version_id, "policy_id": request.policy_id, "version": request.version, "status": "validated", "checksum": checksum}


def publish_policy(store: SecurityStore, actor: Actor, version_id: str, *, confirm: bool) -> dict[str, Any]:
    actor.require("policies:publish")
    if not confirm:
        raise GatewayException("INVALID_REQUEST", detail="publish_requires_confirm")
    row = store.fetch_one("SELECT * FROM security_policy_versions WHERE version_id = ?", (version_id,))
    if not row or row["status"] not in {"validated", "rolled_back", "published"}:
        raise GatewayException("INVALID_REQUEST", detail="policy_version_not_publishable")
    now = utc_now_iso()
    with store.connect() as con:
        con.execute(
            "UPDATE security_policy_versions SET status = 'superseded', updated_at = ? WHERE policy_id = ? AND status = 'published'",
            (now, row["policy_id"]),
        )
        con.execute(
            "UPDATE security_policy_versions SET status = 'published', approved_by = ?, updated_at = ?, published_at = ? WHERE version_id = ?",
            (actor.subject, now, now, version_id),
        )
        con.execute(
            "UPDATE security_policies SET active_version_id = ?, updated_at = ? WHERE policy_id = ?",
            (version_id, now, row["policy_id"]),
        )
    store.audit(
        correlation_id=f"policy-{version_id}",
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="policy_published",
        target_type="security_policy_version",
        target_id=version_id,
        environment=settings.env,
        policy_version=row["version"],
        safe_metadata={"policy_id": row["policy_id"]},
    )
    return {"version_id": version_id, "policy_id": row["policy_id"], "version": row["version"], "status": "published"}


def rollback_policy(store: SecurityStore, actor: Actor, target_version_id: str, *, confirm: bool) -> dict[str, Any]:
    actor.require("policies:publish")
    if not confirm:
        raise GatewayException("INVALID_REQUEST", detail="rollback_requires_confirm")
    row = store.fetch_one("SELECT * FROM security_policy_versions WHERE version_id = ?", (target_version_id,))
    if not row or row["status"] not in {"published", "superseded", "rolled_back"}:
        raise GatewayException("INVALID_REQUEST", detail="policy_version_not_rollback_target")
    now = utc_now_iso()
    with store.connect() as con:
        con.execute(
            "UPDATE security_policy_versions SET status = 'rolled_back', updated_at = ? WHERE policy_id = ? AND status = 'published'",
            (now, row["policy_id"]),
        )
        con.execute(
            "UPDATE security_policy_versions SET status = 'published', updated_at = ?, published_at = COALESCE(published_at, ?) WHERE version_id = ?",
            (now, now, target_version_id),
        )
        con.execute(
            "UPDATE security_policies SET active_version_id = ?, updated_at = ? WHERE policy_id = ?",
            (target_version_id, now, row["policy_id"]),
        )
    store.audit(
        correlation_id=f"policy-{target_version_id}",
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="policy_rolled_back",
        target_type="security_policy_version",
        target_id=target_version_id,
        environment=settings.env,
        policy_version=row["version"],
        safe_metadata={"policy_id": row["policy_id"]},
    )
    return {"version_id": target_version_id, "policy_id": row["policy_id"], "version": row["version"], "status": "published"}


def change_mode(store: SecurityStore, actor: Actor, request: ModeChangeRequest) -> dict[str, Any]:
    actor.require("runtime:write")
    if not request.confirm:
        raise GatewayException("INVALID_REQUEST", detail="mode_change_requires_confirm")
    if request.mode == "enforce":
        active = store.fetch_one(
            """
            SELECT spv.version_id FROM security_policy_versions spv
            JOIN security_policies sp ON sp.active_version_id = spv.version_id
            WHERE spv.status = 'published'
            LIMIT 1
            """
        )
        if not active:
            raise GatewayException("POLICY_UNAVAILABLE", detail="enforce_requires_published_policy")
    updated = store.set_mode(
        mode=request.mode,
        expected_version=request.expected_version,
        actor_subject=actor.subject,
        reason_code="GG_REASON_MODE_CHANGED",
    )
    if not updated:
        raise GatewayException("CONFLICT", detail="mode_version_conflict")
    store.audit(
        correlation_id=f"mode-{updated['version']}",
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="mode_changed",
        target_type="operating_mode_state",
        target_id="global",
        environment=settings.env,
        policy_version=None,
        safe_metadata={"mode": request.mode, "justification": request.justification, "version": updated["version"]},
    )
    return updated


def assign_review(store: SecurityStore, actor: Actor, review_id: str, request: AssignReviewRequest) -> dict[str, Any]:
    actor.require("reviews:write")
    note = redact_text(request.note or "")
    now = utc_now_iso()
    with store.connect() as con:
        current = con.execute("SELECT * FROM manual_reviews WHERE review_id = ?", (review_id,)).fetchone()
        if not current:
            raise GatewayException("INVALID_REQUEST", detail="review_not_found")
        if int(current["version"]) != request.expected_version:
            raise GatewayException("CONFLICT", detail="review_version_conflict")
        con.execute(
            """
            UPDATE manual_reviews
            SET state = 'assigned', assignee = ?, version = version + 1, updated_at = ?
            WHERE review_id = ? AND version = ?
            """,
            (request.assignee, now, review_id, request.expected_version),
        )
        if request.note:
            con.execute(
                "INSERT INTO review_notes(note_id, review_id, actor_subject, note_redacted, created_at) VALUES (?, ?, ?, ?, ?)",
                (f"note_{uuid.uuid4()}", review_id, actor.subject, note.redacted_text, now),
            )
    row = store.fetch_one("SELECT * FROM manual_reviews WHERE review_id = ?", (review_id,))
    store.audit(
        correlation_id=row["correlation_id"],
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="review_assigned",
        target_type="manual_review",
        target_id=review_id,
        environment=settings.env,
        policy_version=None,
        safe_metadata={"assignee": request.assignee},
        redaction_state=note.redaction_state,
    )
    return row


def resolve_review(store: SecurityStore, actor: Actor, review_id: str, request: ResolveReviewRequest) -> dict[str, Any]:
    actor.require("reviews:write")
    if not request.confirm:
        raise GatewayException("INVALID_REQUEST", detail="review_resolution_requires_confirm")
    note = redact_text(request.note)
    now = utc_now_iso()
    with store.connect() as con:
        current = con.execute("SELECT * FROM manual_reviews WHERE review_id = ?", (review_id,)).fetchone()
        if not current:
            raise GatewayException("INVALID_REQUEST", detail="review_not_found")
        if int(current["version"]) != request.expected_version:
            raise GatewayException("CONFLICT", detail="review_version_conflict")
        if current["state"] in {"resolved_allow", "resolved_block", "expired"}:
            raise GatewayException("CONFLICT", detail="review_closed")
        con.execute(
            """
            UPDATE manual_reviews
            SET state = ?, resolution = ?, version = version + 1, updated_at = ?
            WHERE review_id = ? AND version = ?
            """,
            (request.resolution, request.resolution, now, review_id, request.expected_version),
        )
        con.execute(
            "INSERT INTO review_notes(note_id, review_id, actor_subject, note_redacted, created_at) VALUES (?, ?, ?, ?, ?)",
            (f"note_{uuid.uuid4()}", review_id, actor.subject, note.redacted_text, now),
        )
    row = store.fetch_one("SELECT * FROM manual_reviews WHERE review_id = ?", (review_id,))
    store.audit(
        correlation_id=row["correlation_id"],
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="review_resolved" if request.resolution.startswith("resolved") else "review_escalated",
        target_type="manual_review",
        target_id=review_id,
        environment=settings.env,
        policy_version=None,
        safe_metadata={"resolution": request.resolution},
        redaction_state=note.redaction_state,
    )
    return row


def start_review(store: SecurityStore, actor: Actor, review_id: str, request: StartReviewRequest) -> dict[str, Any]:
    actor.require("reviews:write")
    note = redact_text(request.note or "")
    now = utc_now_iso()
    with store.connect() as con:
        current = con.execute("SELECT * FROM manual_reviews WHERE review_id = ?", (review_id,)).fetchone()
        if not current:
            raise GatewayException("INVALID_REQUEST", detail="review_not_found")
        if int(current["version"]) != request.expected_version:
            raise GatewayException("CONFLICT", detail="review_version_conflict")
        if current["state"] not in {"assigned", "pending"}:
            raise GatewayException("CONFLICT", detail="review_not_startable")
        con.execute(
            """
            UPDATE manual_reviews
            SET state = 'in_review', version = version + 1, updated_at = ?
            WHERE review_id = ? AND version = ?
            """,
            (now, review_id, request.expected_version),
        )
        if request.note:
            con.execute(
                "INSERT INTO review_notes(note_id, review_id, actor_subject, note_redacted, created_at) VALUES (?, ?, ?, ?, ?)",
                (f"note_{uuid.uuid4()}", review_id, actor.subject, note.redacted_text, now),
            )
    row = store.fetch_one("SELECT * FROM manual_reviews WHERE review_id = ?", (review_id,))
    store.audit(
        correlation_id=row["correlation_id"],
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="review_started",
        target_type="manual_review",
        target_id=review_id,
        environment=settings.env,
        policy_version=None,
        safe_metadata={"state": "in_review"},
        redaction_state=note.redaction_state,
    )
    return row


def record_sensitive_access(store: SecurityStore, actor: Actor, decision_id: str, *, purpose: str) -> dict[str, Any]:
    actor.require("sensitive:read")
    row = store.fetch_one("SELECT * FROM security_decisions WHERE decision_id = ?", (decision_id,))
    if not row:
        raise GatewayException("INVALID_REQUEST", detail="decision_not_found")
    store.audit(
        correlation_id=row["correlation_id"],
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="sensitive_content_accessed",
        target_type="security_decision",
        target_id=decision_id,
        environment=settings.env,
        policy_version=row["policy_version"],
        safe_metadata={"purpose": purpose, "content_hash": row["content_hash"]},
        redaction_state=row["redaction_state"],
    )
    return {"decision_id": decision_id, "content_hash": row["content_hash"], "restricted_evidence": json.loads(row["restricted_evidence_json"])}
