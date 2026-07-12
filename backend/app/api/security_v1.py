from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.operational.auth import Actor, create_signed_token, require_actor
from app.operational.database import get_store
from app.operational.errors import GatewayException
from app.operational.gateway import create_decision, decision_response_from_row
from app.operational.idempotency import begin_idempotent_request, complete_idempotent_request
from app.operational.observability import metric_summary
from app.operational.rate_limit import check_rate_limit
from app.operational.retention import retention_dry_run
from app.operational.schemas import (
    AssignReviewRequest,
    DevSessionRequest,
    GatewayRequest,
    ModeChangeRequest,
    PolicyDraftRequest,
    PolicyPublishRequest,
    PolicyRollbackRequest,
    ResolveReviewRequest,
    StartReviewRequest,
)
from app.operational.workflows import (
    assign_review,
    change_mode,
    create_policy_draft,
    publish_policy,
    record_sensitive_access,
    resolve_review,
    rollback_policy,
    start_review,
)


router = APIRouter()


def error_response(exc: GatewayException, correlation_id: str | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=exc.spec.status_code,
        content={
            "error": {
                "code": exc.spec.code,
                "message": exc.spec.public_message,
                "retryable": exc.spec.retryable,
                "correlation_id": correlation_id,
            }
        },
        headers={"Retry-After": exc.detail.split(":", 1)[1]} if exc.spec.code == "RATE_LIMITED" and ":" in exc.detail else None,
    )


@router.post("/analyze")
def analyze_gateway(
    request: GatewayRequest,
    actor: Annotated[Actor, Depends(require_actor)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
):
    store = get_store()
    try:
        check_rate_limit(store, actor_scope=actor.client_id, route="analyze")
        payload = request.model_dump(mode="json")
        scope_key, existing = begin_idempotent_request(
            store,
            actor_scope=actor.client_id,
            route="analyze",
            key=idempotency_key,
            request_payload=payload,
        )
        if existing:
            return existing
        result = create_decision(store, actor=actor, request=request, route="analyze", invoke_grader=False)
        response = result.model_dump(mode="json")
        complete_idempotent_request(store, scope_key=scope_key, response_payload=response, target_id=result.decision_id)
        return response
    except GatewayException as exc:
        return error_response(exc, request.correlation_id)


@router.post("/session/dev-token")
def issue_development_token(request: DevSessionRequest):
    if settings.env not in {"development", "test"}:
        return error_response(GatewayException("FORBIDDEN", detail="dev_token_disabled_outside_development"))
    token = create_signed_token(
        subject=request.subject,
        roles=request.roles,
        client_id=request.client_id,
        actor_type="developer_session",
        ttl_seconds=3600,
    )
    return {
        "access_token": token,
        "token_type": "Bearer",
        "expires_in": 3600,
        "subject": request.subject,
        "client_id": request.client_id,
        "roles": request.roles,
        "environment": settings.env,
        "truth_label": "DEVELOPMENT_ONLY_SIGNED_TOKEN",
    }


@router.post("/grade")
def grade_gateway(
    request: GatewayRequest,
    actor: Annotated[Actor, Depends(require_actor)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
):
    store = get_store()
    try:
        check_rate_limit(store, actor_scope=actor.client_id, route="grade")
        payload = request.model_dump(mode="json")
        scope_key, existing = begin_idempotent_request(
            store,
            actor_scope=actor.client_id,
            route="grade",
            key=idempotency_key,
            request_payload=payload,
        )
        if existing:
            return existing
        result = create_decision(store, actor=actor, request=request, route="grade", invoke_grader=True)
        response = result.model_dump(mode="json")
        complete_idempotent_request(store, scope_key=scope_key, response_payload=response, target_id=result.decision_id)
        return response
    except GatewayException as exc:
        return error_response(exc, request.correlation_id)


@router.get("/decisions")
def list_decisions(actor: Annotated[Actor, Depends(require_actor)], limit: int = 100):
    store = get_store()
    try:
        if "decisions:read" not in actor.permissions and "decisions:own_read" not in actor.permissions:
            actor.require("decisions:read")
        limit = min(max(limit, 1), 200)
        if "decisions:read" in actor.permissions:
            rows = store.fetch_all("SELECT * FROM security_decisions ORDER BY created_at DESC LIMIT ?", (limit,))
        else:
            rows = store.fetch_all(
                "SELECT * FROM security_decisions WHERE client_id = ? ORDER BY created_at DESC LIMIT ?",
                (actor.client_id, limit),
            )
        return {"items": [decision_response_from_row(row).model_dump(mode="json") for row in rows]}
    except GatewayException as exc:
        return error_response(exc)


@router.get("/decisions/{decision_id}")
def get_decision(decision_id: str, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        if "decisions:read" not in actor.permissions and "decisions:own_read" not in actor.permissions:
            actor.require("decisions:read")
        row = store.fetch_one("SELECT * FROM security_decisions WHERE decision_id = ?", (decision_id,))
        if not row:
            raise GatewayException("INVALID_REQUEST", detail="decision_not_found")
        if "decisions:own_read" in actor.permissions and "decisions:read" not in actor.permissions and row["client_id"] != actor.client_id:
            raise GatewayException("FORBIDDEN", detail="cross_client_decision_read")
        return decision_response_from_row(row).model_dump(mode="json")
    except GatewayException as exc:
        return error_response(exc)


@router.get("/decisions/{decision_id}/restricted-evidence")
def get_restricted_evidence(decision_id: str, purpose: str, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        return record_sensitive_access(store, actor, decision_id, purpose=purpose)
    except GatewayException as exc:
        return error_response(exc)


@router.get("/incidents")
def list_incidents(actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        actor.require("incidents:read")
        return {"items": store.fetch_all("SELECT * FROM security_incidents ORDER BY opened_at DESC LIMIT 100")}
    except GatewayException as exc:
        return error_response(exc)


@router.get("/incidents/{incident_id}")
def get_incident(incident_id: str, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        actor.require("incidents:read")
        row = store.fetch_one("SELECT * FROM security_incidents WHERE incident_id = ?", (incident_id,))
        if not row:
            raise GatewayException("INVALID_REQUEST", detail="incident_not_found")
        return row
    except GatewayException as exc:
        return error_response(exc)


@router.get("/reviews")
def list_reviews(actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        actor.require("reviews:read")
        return {"items": store.fetch_all("SELECT * FROM manual_reviews ORDER BY updated_at DESC LIMIT 100")}
    except GatewayException as exc:
        return error_response(exc)


@router.post("/reviews/{review_id}/assign")
def assign_review_route(review_id: str, request: AssignReviewRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        return assign_review(store, actor, review_id, request)
    except GatewayException as exc:
        return error_response(exc)


@router.post("/reviews/{review_id}/start")
def start_review_route(review_id: str, request: StartReviewRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        return start_review(store, actor, review_id, request)
    except GatewayException as exc:
        return error_response(exc)


@router.post("/reviews/{review_id}/resolve")
def resolve_review_route(review_id: str, request: ResolveReviewRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        return resolve_review(store, actor, review_id, request)
    except GatewayException as exc:
        return error_response(exc)


@router.get("/policies")
def list_policies(actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        actor.require("policies:read")
        return {"items": store.fetch_all("SELECT * FROM security_policy_versions ORDER BY created_at DESC")}
    except GatewayException as exc:
        return error_response(exc)


@router.post("/policies")
def create_policy(request: PolicyDraftRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        return create_policy_draft(store, actor, request)
    except GatewayException as exc:
        return error_response(exc)


@router.post("/policies/{policy_id}/validate")
def validate_policy(policy_id: str, request: PolicyDraftRequest, actor: Annotated[Actor, Depends(require_actor)]):
    if policy_id != request.policy_id:
        return error_response(GatewayException("INVALID_REQUEST", detail="policy_id_mismatch"))
    return create_policy(request, actor)


@router.post("/policies/{policy_id}/publish")
def publish_policy_route(policy_id: str, request: PolicyPublishRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        result = publish_policy(store, actor, request.version_id, confirm=request.confirm)
        if result["policy_id"] != policy_id:
            raise GatewayException("INVALID_REQUEST", detail="policy_id_mismatch")
        return result
    except GatewayException as exc:
        return error_response(exc)


@router.post("/policies/{policy_id}/rollback")
def rollback_policy_route(policy_id: str, request: PolicyRollbackRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        result = rollback_policy(store, actor, request.target_version_id, confirm=request.confirm)
        if result["policy_id"] != policy_id:
            raise GatewayException("INVALID_REQUEST", detail="policy_id_mismatch")
        return result
    except GatewayException as exc:
        return error_response(exc)


@router.get("/runtime")
def runtime(actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        actor.require("runtime:read")
        return {"mode": store.current_mode(), "metrics": metric_summary(store), "embedding": "unavailable_or_degraded_when_dependency_missing"}
    except GatewayException as exc:
        return error_response(exc)


@router.post("/runtime/mode")
def runtime_mode(request: ModeChangeRequest, actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        return change_mode(store, actor, request)
    except GatewayException as exc:
        return error_response(exc)


@router.get("/retention/dry-run")
def retention(actor: Annotated[Actor, Depends(require_actor)]):
    store = get_store()
    try:
        actor.require("audit:read")
        return retention_dry_run(store).__dict__
    except GatewayException as exc:
        return error_response(exc)


@router.get("/audit")
def list_audit_events(
    actor: Annotated[Actor, Depends(require_actor)],
    target_type: str | None = None,
    target_id: str | None = None,
    correlation_id: str | None = None,
    limit: int = 100,
):
    store = get_store()
    try:
        actor.require("audit:read")
        limit = min(max(limit, 1), 200)
        clauses = []
        params: list[str | int] = []
        if target_type:
            clauses.append("target_type = ?")
            params.append(target_type)
        if target_id:
            clauses.append("target_id = ?")
            params.append(target_id)
        if correlation_id:
            clauses.append("correlation_id = ?")
            params.append(correlation_id)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        rows = store.fetch_all(f"SELECT * FROM audit_events{where} ORDER BY created_at ASC LIMIT ?", (*params, limit))
        return {"items": rows}
    except GatewayException as exc:
        return error_response(exc)


@router.get("/health/live")
def live():
    return {"status": "live", "service": "gradingguard-ai"}


@router.get("/health/ready")
def ready():
    store = get_store()
    mode = store.current_mode()
    return {
        "status": "ready",
        "database": "reachable",
        "schema_version": 1,
        "mode": mode["mode"],
        "audit_persistence": "available",
        "embedding": "truthful_unavailable_when_missing",
    }


@router.options("/{path:path}")
def preflight(path: str, request: Request):
    return {"status": "ok", "path": path}
