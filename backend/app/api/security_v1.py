from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.responses import JSONResponse

from app.operational.auth import Actor, require_actor
from app.operational.database import get_store
from app.operational.errors import GatewayException
from app.operational.gateway import create_decision, decision_response_from_row
from app.operational.idempotency import begin_idempotent_request, complete_idempotent_request
from app.operational.observability import metric_summary
from app.operational.rate_limit import check_rate_limit
from app.operational.retention import retention_dry_run
from app.operational.schemas import (
    AssignReviewRequest,
    GatewayRequest,
    ModeChangeRequest,
    PolicyDraftRequest,
    PolicyPublishRequest,
    PolicyRollbackRequest,
    ResolveReviewRequest,
)
from app.operational.workflows import (
    assign_review,
    change_mode,
    create_policy_draft,
    publish_policy,
    record_sensitive_access,
    resolve_review,
    rollback_policy,
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

