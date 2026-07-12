from __future__ import annotations

import hashlib
import json
import time
import uuid
from datetime import UTC, timedelta
from typing import Any

from app.config import settings
from app.firewall.schemas import FirewallAnalyzeRequest
from app.firewall.service import analyze_submission
from app.grader.mock_grader import build_protected_grader_request, mock_grade
from app.operational.auth import Actor
from app.operational.correlation import resolve_correlation_id
from app.operational.database import SecurityStore
from app.operational.errors import GatewayException
from app.operational.observability import record_metric, safe_log
from app.operational.redaction import redact_text
from app.operational.schemas import GatewayDecisionResponse, GatewayRequest
from app.operational.time import utc_now, utc_now_iso


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _checksum(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def active_policy(store: SecurityStore) -> dict[str, Any]:
    row = store.fetch_one(
        """
        SELECT spv.*, sp.name
        FROM security_policy_versions spv
        JOIN security_policies sp ON sp.policy_id = spv.policy_id
        WHERE sp.active_version_id = spv.version_id
        LIMIT 1
        """
    )
    if row:
        return row
    return {
        "policy_id": "static_phase4_policy",
        "version": "phase4_static_shadow_v1",
        "version_id": "static_phase4_policy:phase4_static_shadow_v1",
        "status": "published",
    }


def detector_health_summary(contributions: list[dict[str, Any]]) -> dict[str, str]:
    return {str(item.get("detector_id", "unknown")): str(item.get("runtime_health", "unknown")) for item in contributions}


def create_decision(
    store: SecurityStore,
    *,
    actor: Actor,
    request: GatewayRequest,
    route: str = "analyze",
    invoke_grader: bool = False,
) -> GatewayDecisionResponse:
    actor.require("gateway:submit")
    start = time.perf_counter()
    correlation_id = resolve_correlation_id(request.correlation_id)
    now = utc_now_iso()
    mode_row = store.current_mode()
    mode = str(mode_row["mode"])
    policy = active_policy(store)
    redaction = redact_text(request.candidate_content)
    decision_id = f"dec_{uuid.uuid4()}"

    store.audit(
        correlation_id=correlation_id,
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="request_received",
        target_type="security_decision",
        target_id=decision_id,
        environment=settings.env,
        policy_version=str(policy["version"]),
        safe_metadata={"route": route, "request_id": request.request_id, "client_id": actor.client_id},
        redaction_state=redaction.redaction_state,
    )

    firewall = analyze_submission(
        FirewallAnalyzeRequest(text=request.candidate_content, task_type=request.task_type),
        mode=mode,
    )
    health = detector_health_summary(firewall.detector_contributions)
    techniques = sorted({str(t) for item in firewall.detector_contributions for t in item.get("technique_ids", []) if t})
    applied_action = firewall.action
    counterfactual = firewall.counterfactual_action
    final_outcome = "allowed"
    review_state = None
    grader_metadata: dict[str, Any] = {"adapter": "not_invoked", "score_integrity_status": "NOT_MEASURED"}

    if applied_action == "block":
        final_outcome = "blocked"
    elif applied_action == "manual_review" or counterfactual in {"manual_review", "block"}:
        final_outcome = "review_recommended" if mode == "shadow" else "review_required"
        review_state = "pending"
    elif invoke_grader or applied_action == "secure_grade":
        build_protected_grader_request(request.candidate_content)
        result = mock_grade(request.candidate_content, mode="secure")
        grader_metadata = {
            "adapter": "DeterministicDemoGrader",
            "adapter_version": "phase4_demo_adapter_v1",
            "score_integrity_status": "DETERMINISTIC_DEMO",
            "overall_band": result.overall_band,
        }
        final_outcome = "graded_demo"

    completed = utc_now_iso()
    latency_ms = round((time.perf_counter() - start) * 1000, 3)
    restricted_evidence = {
        "detector_contributions": firewall.detector_contributions,
        "detected_patterns": firewall.detected_patterns,
        "normalization_flags": firewall.normalization_flags,
        "content_hash": redaction.content_hash,
        "redacted_counts": redaction.redacted_counts,
    }

    with store.connect() as con:
        con.execute(
            """
            INSERT INTO security_decisions(
              decision_id, request_id, correlation_id, client_id, submission_id, pseudonymous_user_id,
              task_type, language, operating_mode, risk_score, severity, techniques_json, detector_health_json,
              selected_action, counterfactual_action, policy_id, policy_version, grader_status, review_state,
              final_outcome, latency_ms, redaction_state, safe_preview, content_hash, restricted_evidence_json,
              created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                decision_id,
                request.request_id,
                correlation_id,
                actor.client_id,
                request.submission_id,
                request.pseudonymous_user_id,
                request.task_type,
                request.language,
                mode,
                firewall.risk_score,
                firewall.risk_level,
                _json(techniques),
                _json(health),
                applied_action,
                counterfactual,
                str(policy["policy_id"]),
                str(policy["version"]),
                str(grader_metadata["adapter"]),
                review_state or "none",
                final_outcome,
                latency_ms,
                redaction.redaction_state,
                redaction.preview,
                redaction.content_hash,
                _json(restricted_evidence),
                now,
                completed,
            ),
        )
        for item in firewall.detector_contributions:
            con.execute(
                """
                INSERT INTO detector_results(
                  detector_result_id, decision_id, detector_id, runtime_health, score_contribution, confidence,
                  techniques_json, safe_evidence_json, latency_ms, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    f"det_{uuid.uuid4()}",
                    decision_id,
                    str(item.get("detector_id", "unknown")),
                    str(item.get("runtime_health", "unknown")),
                    float(item.get("score_contribution", 0.0)),
                    float(item.get("confidence", 0.0)),
                    _json(item.get("technique_ids", [])),
                    _json({"evidence_refs": item.get("evidence_spans", [])}),
                    float(item.get("latency_ms", 0.0)),
                    completed,
                ),
            )

    store.audit(
        correlation_id=correlation_id,
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="detector_result",
        target_type="security_decision",
        target_id=decision_id,
        environment=settings.env,
        policy_version=str(policy["version"]),
        safe_metadata={"detector_health": health, "risk_score": firewall.risk_score},
        redaction_state=redaction.redaction_state,
    )
    store.audit(
        correlation_id=correlation_id,
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="policy_evaluated",
        target_type="security_decision",
        target_id=decision_id,
        environment=settings.env,
        policy_version=str(policy["version"]),
        safe_metadata={"mode": mode, "applied_action": applied_action, "counterfactual_action": counterfactual},
        redaction_state=redaction.redaction_state,
        reason_code=firewall.public_reason_code,
    )

    incident_id = None
    review_id = None
    if review_state == "pending":
        incident_id, review_id = create_incident_and_review(
            store,
            actor=actor,
            decision_id=decision_id,
            correlation_id=correlation_id,
            severity=firewall.risk_level,
            techniques=techniques,
            selected_action=applied_action,
            safe_preview=redaction.preview,
            policy_version=str(policy["version"]),
        )

    store.audit(
        correlation_id=correlation_id,
        actor_subject=actor.subject,
        actor_type=actor.actor_type,
        action="decision_made",
        target_type="security_decision",
        target_id=decision_id,
        environment=settings.env,
        policy_version=str(policy["version"]),
        safe_metadata={"action": applied_action, "final_outcome": final_outcome, "incident_id": incident_id, "review_id": review_id},
        redaction_state=redaction.redaction_state,
        reason_code=firewall.public_reason_code,
    )
    record_metric(store, "gateway_request_count", 1, {"route": route, "action": applied_action, "severity": firewall.risk_level, "mode": mode})
    record_metric(store, "gateway_request_latency_ms", latency_ms, {"route": route, "action": applied_action, "mode": mode})
    safe_log(
        20,
        "gateway_decision_completed",
        correlation_id=correlation_id,
        route=route,
        action=applied_action,
        mode=mode,
        risk_band=firewall.risk_level,
    )

    return GatewayDecisionResponse(
        decision_id=decision_id,
        request_id=request.request_id,
        correlation_id=correlation_id,
        operating_mode=mode,
        applied_action=applied_action,
        counterfactual_action=counterfactual,
        risk_score=firewall.risk_score,
        severity=firewall.risk_level,
        detected_techniques=techniques,
        policy_id=str(policy["policy_id"]),
        policy_version=str(policy["version"]),
        detector_health=health,
        review_state=review_state,
        incident_id=incident_id,
        review_id=review_id,
        final_outcome=final_outcome,
        grader_result_metadata=grader_metadata,
        safe_preview=redaction.preview,
        redaction_state=redaction.redaction_state,
        retryable=False,
        created_at=now,
        completed_at=completed,
    )


def create_incident_and_review(
    store: SecurityStore,
    *,
    actor: Actor,
    decision_id: str,
    correlation_id: str,
    severity: str,
    techniques: list[str],
    selected_action: str,
    safe_preview: str,
    policy_version: str,
) -> tuple[str, str]:
    incident_id = f"inc_{uuid.uuid4()}"
    review_id = f"rev_{uuid.uuid4()}"
    now_dt = utc_now()
    now = now_dt.isoformat().replace("+00:00", "Z")
    sla = (now_dt + timedelta(hours=24)).astimezone(UTC).isoformat().replace("+00:00", "Z")
    with store.connect() as con:
        con.execute(
            """
            INSERT INTO security_incidents(
              incident_id, decision_id, correlation_id, severity, status, techniques_json, selected_action,
              assignee, opened_at, updated_at, resolved_at, resolution, safe_summary, restricted_evidence_ref
            ) VALUES (?, ?, ?, ?, 'awaiting_review', ?, ?, NULL, ?, ?, NULL, NULL, ?, ?)
            """,
            (incident_id, decision_id, correlation_id, severity, _json(techniques), selected_action, now, now, safe_preview, decision_id),
        )
        con.execute(
            """
            INSERT INTO manual_reviews(
              review_id, decision_id, incident_id, correlation_id, state, priority, sla_deadline, assignee,
              safe_content_preview, resolution, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'pending', ?, ?, NULL, ?, NULL, ?, ?)
            """,
            (review_id, decision_id, incident_id, correlation_id, "high" if severity in {"high", "critical"} else "normal", sla, safe_preview, now, now),
        )
    for action, target, target_id in [
        ("incident_created", "security_incident", incident_id),
        ("review_created", "manual_review", review_id),
    ]:
        store.audit(
            correlation_id=correlation_id,
            actor_subject=actor.subject,
            actor_type=actor.actor_type,
            action=action,
            target_type=target,
            target_id=target_id,
            environment=settings.env,
            policy_version=policy_version,
            safe_metadata={"decision_id": decision_id, "severity": severity},
            reason_code="GG_REASON_REVIEW_RECOMMENDED",
        )
    return incident_id, review_id


def decision_response_from_row(row: dict[str, Any]) -> GatewayDecisionResponse:
    return GatewayDecisionResponse(
        decision_id=row["decision_id"],
        request_id=row["request_id"],
        correlation_id=row["correlation_id"],
        operating_mode=row["operating_mode"],
        applied_action=row["selected_action"],
        counterfactual_action=row["counterfactual_action"],
        risk_score=float(row["risk_score"]),
        severity=row["severity"],
        detected_techniques=json.loads(row["techniques_json"]),
        policy_id=row["policy_id"],
        policy_version=row["policy_version"],
        detector_health=json.loads(row["detector_health_json"]),
        review_state=None if row["review_state"] == "none" else row["review_state"],
        final_outcome=row["final_outcome"],
        grader_result_metadata={"adapter": row["grader_status"], "score_integrity_status": "DETERMINISTIC_DEMO" if "Demo" in row["grader_status"] else "NOT_MEASURED"},
        safe_preview=row["safe_preview"],
        redaction_state=row["redaction_state"],
        retryable=False,
        created_at=row["created_at"],
        completed_at=row["updated_at"],
    )

