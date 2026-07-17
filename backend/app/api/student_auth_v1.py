from __future__ import annotations

import hashlib
import secrets
import time
import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.config import settings
from app.operational.auth import Actor
from app.operational.database import get_store
from app.operational.errors import ERRORS, GatewayException
from app.operational.gateway import create_decision
from app.operational.rate_limit import check_rate_limit
from app.operational.schemas import GatewayRequest
from app.student_auth import repository
from app.student_auth.passwords import hash_password, verify_password
from app.student_auth.tokens import StudentTokenPayload, create_student_access_token, verify_student_access_token

router = APIRouter()


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=32)


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class StudentAnalyzeRequest(BaseModel):
    """Student-facing analyze request. Deliberately has no field for the
    caller to assert their own identity (no pseudonymous_user_id, no
    student_id, no actor/client_id) -- extra="forbid" rejects any request
    that tries to smuggle one in. The authenticated student_id is bound
    server-side in the analyze() handler below, from require_student's
    verified token, never from this payload."""

    model_config = ConfigDict(extra="forbid")

    submission_id: str = Field(..., min_length=1, max_length=128)
    task_type: Literal["writing", "speaking"] = "writing"
    candidate_content: str = Field(..., min_length=1)
    language: str = Field(default="en", min_length=2, max_length=16, pattern=r"^[A-Za-z]{2,3}(?:-[A-Za-z0-9]{2,8})?$")


def _error_response(code: str) -> JSONResponse:
    spec = ERRORS[code]
    return JSONResponse(
        status_code=spec.status_code,
        content={"error": {"code": spec.code, "message": spec.public_message, "retryable": spec.retryable}},
    )


def _hash_refresh_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _set_session_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        settings.student_session_cookie_name,
        access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.student_access_token_ttl_seconds,
    )
    response.set_cookie(
        settings.student_refresh_cookie_name,
        refresh_token,
        httponly=True,
        samesite="lax",
        max_age=settings.student_refresh_token_ttl_seconds,
    )


@router.post("/register", status_code=201)
def register(payload: RegisterRequest):
    store = get_store()
    try:
        student_id = repository.create_student(
            store,
            email=payload.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            phone=payload.phone,
        )
    except ValueError:
        return _error_response("EMAIL_ALREADY_EXISTS")
    return {"id": student_id, "email": payload.email, "full_name": payload.full_name}


@router.post("/login")
def login(payload: LoginRequest, request: Request, response: Response):
    store = get_store()
    student = repository.find_student_by_email(store, payload.email)
    if student is None or not verify_password(payload.password, student["password_hash"]):
        return _error_response("INVALID_CREDENTIALS")

    refresh_token = secrets.token_urlsafe(32)
    session_id = repository.try_create_session_within_limit(
        store,
        student_id=student["id"],
        refresh_token_hash=_hash_refresh_token(refresh_token),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        ttl_seconds=settings.student_refresh_token_ttl_seconds,
        max_devices=settings.student_max_devices,
    )
    if session_id is None:
        return _error_response("DEVICE_LIMIT_EXCEEDED")

    access_token = create_student_access_token(student_id=student["id"], email=student["email"])
    _set_session_cookies(response, access_token, refresh_token)
    return {"id": student["id"], "email": student["email"], "full_name": student["full_name"]}


@router.post("/logout")
def logout(request: Request, response: Response):
    store = get_store()
    raw_refresh = request.cookies.get(settings.student_refresh_cookie_name)
    if raw_refresh:
        session = repository.find_session_by_refresh_hash(store, _hash_refresh_token(raw_refresh))
        if session:
            repository.revoke_session(store, session["id"])
    response.delete_cookie(settings.student_session_cookie_name)
    response.delete_cookie(settings.student_refresh_cookie_name)
    return {"ok": True}


@router.post("/refresh")
def refresh(request: Request, response: Response):
    store = get_store()
    raw_refresh = request.cookies.get(settings.student_refresh_cookie_name)
    if not raw_refresh:
        return _error_response("INVALID_CREDENTIALS")
    session = repository.find_session_by_refresh_hash(store, _hash_refresh_token(raw_refresh))
    if session is None:
        return _error_response("INVALID_CREDENTIALS")
    row = store.fetch_one("SELECT * FROM students WHERE id = ?", (session["student_id"],))
    if row is None:
        return _error_response("INVALID_CREDENTIALS")
    repository.touch_session(store, session["id"])
    access_token = create_student_access_token(student_id=row["id"], email=row["email"])
    response.set_cookie(
        settings.student_session_cookie_name,
        access_token,
        httponly=True,
        samesite="lax",
        max_age=settings.student_access_token_ttl_seconds,
    )
    return {"ok": True}


def require_student(request: Request) -> StudentTokenPayload:
    token = request.cookies.get(settings.student_session_cookie_name)
    if not token:
        raise GatewayException("UNAUTHORIZED", detail="student_session_cookie_missing")
    try:
        return verify_student_access_token(token)
    except ValueError as exc:
        raise GatewayException("UNAUTHORIZED", detail="student_session_token_invalid") from exc


@router.get("/me")
def me(student: Annotated[StudentTokenPayload, Depends(require_student)]):
    return {"id": student.student_id, "email": student.email}


@router.get("/devices")
def list_devices(student: Annotated[StudentTokenPayload, Depends(require_student)]):
    store = get_store()
    sessions = repository.list_active_sessions(store, student.student_id)
    return {"devices": sessions}


@router.post("/devices/{session_id}/revoke")
def revoke_device(session_id: str, student: Annotated[StudentTokenPayload, Depends(require_student)]):
    store = get_store()
    sessions = repository.list_active_sessions(store, student.student_id)
    if not any(s["id"] == session_id for s in sessions):
        return _error_response("INVALID_CREDENTIALS")
    repository.revoke_session(store, session_id)
    return {"ok": True}


_STUDENT_GATEWAY_ACTOR_ROLES = ("integration_service",)


def _build_student_gateway_actor(student: StudentTokenPayload) -> Actor:
    """A synthetic operator-shaped Actor used only to satisfy create_decision's
    signature. It carries no real operator credentials and is never derived
    from a signed token -- it exists solely so the student-auth layer can
    reuse the existing grading/firewall pipeline without touching gateway.py
    or security_v1.py. Its only meaningful permission is gateway:submit."""
    now = int(time.time())
    return Actor(
        subject=f"student:{student.student_id}",
        actor_type="student_session",
        roles=_STUDENT_GATEWAY_ACTOR_ROLES,
        client_id=f"student-{student.student_id}",
        tenant="local",
        issued_at=now,
        expires_at=now + 1,
    )


@router.post("/analyze")
def analyze(payload: StudentAnalyzeRequest, student: Annotated[StudentTokenPayload, Depends(require_student)]):
    store = get_store()
    actor = _build_student_gateway_actor(student)
    gateway_request = GatewayRequest(
        request_id=f"stu-{uuid.uuid4().hex}",
        submission_id=payload.submission_id,
        pseudonymous_user_id=student.student_id,
        task_type=payload.task_type,
        candidate_content=payload.candidate_content,
        language=payload.language,
    )
    try:
        check_rate_limit(store, actor_scope=actor.client_id, route="student_analyze")
        result = create_decision(store, actor=actor, request=gateway_request, route="student_analyze", invoke_grader=False)
        return result.model_dump(mode="json")
    except GatewayException as exc:
        spec = exc.spec
        return JSONResponse(
            status_code=spec.status_code,
            content={"error": {"code": spec.code, "message": spec.public_message, "retryable": spec.retryable}},
        )


@router.get("/submissions")
def list_submissions(student: Annotated[StudentTokenPayload, Depends(require_student)]):
    store = get_store()
    rows = store.fetch_all(
        """
        SELECT decision_id, request_id, selected_action AS applied_action, risk_score, severity, created_at
        FROM security_decisions
        WHERE pseudonymous_user_id = ?
        ORDER BY created_at DESC
        LIMIT 50
        """,
        (student.student_id,),
    )
    return {"submissions": rows}
