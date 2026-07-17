from __future__ import annotations

import hashlib
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.config import settings
from app.operational.database import get_store
from app.operational.errors import ERRORS
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

    active_count = repository.count_active_sessions(store, student["id"])
    if active_count >= settings.student_max_devices:
        return _error_response("DEVICE_LIMIT_EXCEEDED")

    refresh_token = secrets.token_urlsafe(32)
    repository.create_session(
        store,
        student_id=student["id"],
        refresh_token_hash=_hash_refresh_token(refresh_token),
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
        ttl_seconds=settings.student_refresh_token_ttl_seconds,
    )
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
        raise HTTPException(
            status_code=401,
            detail={"error": {"code": "UNAUTHORIZED", "message": "Login required.", "retryable": False}},
        )
    try:
        return verify_student_access_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {"code": "UNAUTHORIZED", "message": "Session expired or invalid.", "retryable": False}
            },
        ) from exc


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
