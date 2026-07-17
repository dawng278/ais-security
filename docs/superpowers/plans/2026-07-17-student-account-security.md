# Bảo mật tài khoản học viên (giới hạn 2 thiết bị) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cho học viên đăng ký/đăng nhập bằng email+mật khẩu, giới hạn tối đa 2 thiết bị đăng nhập đồng thời (từ chối thiết bị thứ 3), và gắn lịch sử bài làm ở `/playground` với tài khoản học viên thay vì ẩn danh.

**Architecture:** Module backend mới `backend/app/student_auth/` (song song với `backend/app/operational/`, không sửa file operator hiện có) dùng lại cùng SQLite DB qua `SecurityStore` đã có, thêm 2 bảng `students`/`student_sessions` vào `SCHEMA_SQL`. Router FastAPI mới `student_auth_v1.py` theo đúng pattern `security_v1.py`. Access token JWT-like ký HMAC-SHA256 riêng (secret riêng, không dùng chung với operator), lưu qua httpOnly cookie. Frontend thêm `/login`, `/register`, `/account/devices`, sửa `/playground` để yêu cầu đăng nhập.

**Tech Stack:** FastAPI, SQLite (`sqlite3` chuẩn qua `SecurityStore`), bcrypt (mới), Next.js App Router (client components), `fetch` API.

## Global Constraints

- Không sửa `backend/app/operational/auth.py`, `backend/app/api/security_v1.py`, hoặc bất kỳ file nào trong `backend/app/firewall/`.
- Đăng nhập bằng email + mật khẩu. Mật khẩu hash bằng bcrypt, không bao giờ lưu/trả plaintext.
- 1 lần đăng nhập = 1 session/thiết bị. Tối đa 2 session sống đồng thời/học viên. Vượt quá → từ chối đăng nhập thiết bị thứ 3 (HTTP 409, không tự động revoke thiết bị cũ).
- Access token: JWT-like ký HMAC-SHA256, TTL ngắn (mặc định 30 phút). Refresh token: TTL dài (mặc định 7 ngày), lưu dạng hash trong DB (không lưu plaintext).
- Cả access token và refresh token set qua httpOnly cookie (không lưu localStorage).
- PII (tên, email, sđt) lưu plaintext trong SQLite — không mã hóa at-rest. Không bao giờ trả `password_hash` hoặc raw token qua response JSON hay log.
- Không thêm ORM mới — dùng `SecurityStore.connect()/fetch_one()/fetch_all()/execute()` đã có trong `backend/app/operational/database.py`.
- Thêm 1 dependency mới: `bcrypt` vào `backend/requirements.txt`.

---

## Task 1: Schema DB — bảng `students` và `student_sessions`

**Files:**
- Modify: `backend/app/operational/database.py` (thêm vào `SCHEMA_SQL`, list bắt đầu dòng 37, kết thúc dòng 253)
- Test: `backend/tests/test_student_auth_schema.py`

**Interfaces:**
- Produces: bảng SQLite `students(id, email, password_hash, full_name, phone, created_at)` và `student_sessions(id, student_id, refresh_token_hash, user_agent, ip_address, created_at, last_seen_at, expires_at, revoked_at)`, index `idx_student_sessions_student` trên `student_sessions(student_id, revoked_at, expires_at)`. Các task sau dùng `get_store()` để truy vấn 2 bảng này qua raw SQL.

- [ ] **Step 1: Viết test thất bại xác nhận bảng chưa tồn tại**

```python
# backend/tests/test_student_auth_schema.py
from __future__ import annotations

from pathlib import Path

import pytest

from app.config import settings
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests


@pytest.fixture()
def store(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'schema_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield get_store()
    settings.test_database_url = None


def test_students_table_exists(store):
    with store.connect() as con:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
        ).fetchone()
    assert row is not None


def test_student_sessions_table_exists(store):
    with store.connect() as con:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='student_sessions'"
        ).fetchone()
    assert row is not None


def test_student_sessions_has_expected_columns(store):
    with store.connect() as con:
        cols = {r[1] for r in con.execute("PRAGMA table_info(student_sessions)").fetchall()}
    assert cols == {
        "id",
        "student_id",
        "refresh_token_hash",
        "user_agent",
        "ip_address",
        "created_at",
        "last_seen_at",
        "expires_at",
        "revoked_at",
    }
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_auth_schema.py -v`
Expected: FAIL — bảng `students`/`student_sessions` chưa tồn tại (assert `row is not None` thất bại).

- [ ] **Step 3: Thêm 2 bảng mới vào `SCHEMA_SQL`**

Mở `backend/app/operational/database.py`, tìm phần tử cuối cùng của list `SCHEMA_SQL` (ngay trước dấu `]` đóng list ở dòng 253), thêm các string SQL sau vào cuối list (theo đúng style `CREATE TABLE IF NOT EXISTS` các bảng khác trong file, PK/FK là `TEXT`, timestamp là `TEXT` ISO):

```python
    """
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        phone TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS student_sessions (
        id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL REFERENCES students(id),
        refresh_token_hash TEXT NOT NULL,
        user_agent TEXT,
        ip_address TEXT,
        created_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        revoked_at TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_student_sessions_student ON student_sessions(student_id, revoked_at, expires_at)",
```

- [ ] **Step 4: Chạy test, xác nhận thành công**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_auth_schema.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
cd backend
git add app/operational/database.py tests/test_student_auth_schema.py
git commit -m "feat(student-auth): add students and student_sessions tables"
```

---

## Task 2: Password hashing (bcrypt)

**Files:**
- Create: `backend/app/student_auth/__init__.py` (rỗng)
- Create: `backend/app/student_auth/passwords.py`
- Modify: `backend/requirements.txt`
- Test: `backend/tests/test_student_passwords.py`

**Interfaces:**
- Produces: `hash_password(plain: str) -> str`, `verify_password(plain: str, hashed: str) -> bool` — dùng bởi Task 4 (register) và Task 5 (login).

- [ ] **Step 1: Thêm bcrypt vào requirements.txt**

Mở `backend/requirements.txt`, thêm dòng mới vào cuối file:

```
bcrypt>=4.2.0
```

Cài đặt:
Run: `cd backend && ./venv/bin/pip install bcrypt>=4.2.0`
Expected: `Successfully installed bcrypt-...`

- [ ] **Step 2: Viết test thất bại cho hash/verify**

```python
# backend/tests/test_student_passwords.py
from __future__ import annotations

from app.student_auth.passwords import hash_password, verify_password


def test_hash_password_produces_different_output_than_input():
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"
    assert len(hashed) > 20


def test_verify_password_accepts_correct_password():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", hashed) is False


def test_hash_password_is_salted():
    a = hash_password("same-password")
    b = hash_password("same-password")
    assert a != b
```

- [ ] **Step 3: Chạy test, xác nhận thất bại**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_passwords.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.student_auth.passwords'`

- [ ] **Step 4: Tạo package và implement**

Tạo file rỗng `backend/app/student_auth/__init__.py`.

```python
# backend/app/student_auth/passwords.py
from __future__ import annotations

import bcrypt


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```

- [ ] **Step 5: Chạy test, xác nhận thành công**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_passwords.py -v`
Expected: PASS (4 tests)

- [ ] **Step 6: Commit**

```bash
cd backend
git add app/student_auth/__init__.py app/student_auth/passwords.py requirements.txt tests/test_student_passwords.py
git commit -m "feat(student-auth): add bcrypt password hashing"
```

---

## Task 3: Cấu hình settings mới

**Files:**
- Modify: `backend/app/config.py`

**Interfaces:**
- Produces: `settings.student_token_secret: str`, `settings.student_access_token_ttl_seconds: int`, `settings.student_refresh_token_ttl_seconds: int`, `settings.student_max_devices: int`, `settings.student_session_cookie_name: str`, `settings.student_refresh_cookie_name: str` — dùng bởi Task 4, 5, 6.

- [ ] **Step 1: Thêm field mới vào class `Settings`**

Mở `backend/app/config.py`, thêm các dòng sau vào cuối class `Settings` (sau `rate_limit_max_requests: int = 120`, trước dòng trống cuối class):

```python
    student_token_secret: str = "student-development-only-change-me"
    student_access_token_ttl_seconds: int = 1800
    student_refresh_token_ttl_seconds: int = 604800
    student_max_devices: int = 2
    student_session_cookie_name: str = "gg_student_access"
    student_refresh_cookie_name: str = "gg_student_refresh"
```

- [ ] **Step 2: Xác nhận import thành công**

Run: `cd backend && ./venv/bin/python -c "from app.config import settings; print(settings.student_max_devices, settings.student_token_secret)"`
Expected: `2 student-development-only-change-me`

- [ ] **Step 3: Commit**

```bash
cd backend
git add app/config.py
git commit -m "feat(student-auth): add student auth configuration settings"
```

---

## Task 4: Token JWT-like riêng cho học viên

**Files:**
- Create: `backend/app/student_auth/tokens.py`
- Test: `backend/tests/test_student_tokens.py`

**Interfaces:**
- Consumes: `settings.student_token_secret`, `settings.student_access_token_ttl_seconds` (Task 3)
- Produces: dataclass `StudentTokenPayload(student_id: str, email: str)`; `create_student_access_token(student_id: str, email: str, ttl_seconds: int | None = None) -> str`; `verify_student_access_token(token: str) -> StudentTokenPayload` (raise `ValueError` nếu invalid/hết hạn). Dùng bởi Task 6 (middleware `require_student`) và Task 5 (login response).

- [ ] **Step 1: Viết test thất bại**

```python
# backend/tests/test_student_tokens.py
from __future__ import annotations

import time

import pytest

from app.student_auth.tokens import create_student_access_token, verify_student_access_token


def test_create_and_verify_roundtrip():
    token = create_student_access_token(student_id="stu-1", email="a@example.com")
    payload = verify_student_access_token(token)
    assert payload.student_id == "stu-1"
    assert payload.email == "a@example.com"


def test_verify_rejects_tampered_token():
    token = create_student_access_token(student_id="stu-1", email="a@example.com")
    tampered = token[:-4] + "abcd"
    with pytest.raises(ValueError):
        verify_student_access_token(tampered)


def test_verify_rejects_expired_token():
    token = create_student_access_token(student_id="stu-1", email="a@example.com", ttl_seconds=-1)
    with pytest.raises(ValueError):
        verify_student_access_token(token)


def test_verify_rejects_malformed_token():
    with pytest.raises(ValueError):
        verify_student_access_token("not-a-valid-token")
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_tokens.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.student_auth.tokens'`

- [ ] **Step 3: Implement**

```python
# backend/app/student_auth/tokens.py
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


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _sign(message: str, secret: str) -> str:
    return _b64url_encode(hmac.new(secret.encode("utf-8"), message.encode("ascii"), hashlib.sha256).digest())


def create_student_access_token(student_id: str, email: str, ttl_seconds: int | None = None) -> str:
    ttl = settings.student_access_token_ttl_seconds if ttl_seconds is None else ttl_seconds
    now = int(time.time())
    header = {"alg": "HS256", "typ": "GGSTU"}
    payload = {
        "sub": student_id,
        "email": email,
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
    return StudentTokenPayload(student_id=payload["sub"], email=payload["email"])
```

- [ ] **Step 4: Chạy test, xác nhận thành công**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_tokens.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
cd backend
git add app/student_auth/tokens.py tests/test_student_tokens.py
git commit -m "feat(student-auth): add HMAC-signed student access tokens"
```

---

## Task 5: Error codes mới cho student flow

**Files:**
- Modify: `backend/app/operational/errors.py`

**Interfaces:**
- Produces: `ERRORS["DEVICE_LIMIT_EXCEEDED"]`, `ERRORS["EMAIL_ALREADY_EXISTS"]`, `ERRORS["INVALID_CREDENTIALS"]` — dùng bởi Task 6 (router).

- [ ] **Step 1: Thêm error spec mới**

Mở `backend/app/operational/errors.py`, thêm vào dict `ERRORS` (trước dòng đóng `}` ở dòng 35):

```python
    "DEVICE_LIMIT_EXCEEDED": GatewayErrorSpec(
        "DEVICE_LIMIT_EXCEEDED", 409, False,
        "You are already logged in on 2 devices. Log out from one device to continue.",
        "STUDENT_DEVICE_LIMIT_EXCEEDED",
    ),
    "EMAIL_ALREADY_EXISTS": GatewayErrorSpec(
        "EMAIL_ALREADY_EXISTS", 409, False,
        "An account with this email already exists.",
        "STUDENT_EMAIL_DUPLICATE",
    ),
    "INVALID_CREDENTIALS": GatewayErrorSpec(
        "INVALID_CREDENTIALS", 401, False,
        "Email or password is incorrect.",
        "STUDENT_INVALID_CREDENTIALS",
    ),
```

- [ ] **Step 2: Xác nhận import thành công**

Run: `cd backend && ./venv/bin/python -c "from app.operational.errors import ERRORS; print(ERRORS['DEVICE_LIMIT_EXCEEDED'].status_code)"`
Expected: `409`

- [ ] **Step 3: Commit**

```bash
cd backend
git add app/operational/errors.py
git commit -m "feat(student-auth): add student-specific error codes"
```

---

## Task 6: Router `student_auth_v1` — register, login, logout, refresh

**Files:**
- Create: `backend/app/student_auth/repository.py`
- Create: `backend/app/api/student_auth_v1.py`
- Modify: `backend/app/main.py`
- Test: `backend/tests/test_student_auth_v1.py`

**Interfaces:**
- Consumes: `get_store()` (từ `app.operational.database`), `hash_password/verify_password` (Task 2), `create_student_access_token/verify_student_access_token` (Task 4), `ERRORS` (Task 5), `settings.student_*` (Task 3)
- Produces: `repository.create_student(email, password_hash, full_name, phone) -> str` (trả student_id, raise `ValueError("email_exists")` nếu trùng); `repository.find_student_by_email(email) -> dict | None`; `repository.count_active_sessions(student_id) -> int`; `repository.create_session(student_id, refresh_token_hash, user_agent, ip_address, ttl_seconds) -> str` (trả session_id); `repository.find_session_by_refresh_hash(refresh_token_hash) -> dict | None`; `repository.revoke_session(session_id) -> None`; `repository.touch_session(session_id) -> None`. Router expose `POST /api/v1/students/register`, `POST /api/v1/students/login`, `POST /api/v1/students/logout`, `POST /api/v1/students/refresh` — dùng bởi Task 8 (frontend `student-api.ts`).

- [ ] **Step 1: Viết test thất bại cho luồng register + login + giới hạn 2 thiết bị**

```python
# backend/tests/test_student_auth_v1.py
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'student_auth_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield TestClient(app)
    settings.test_database_url = None


def register(client, email="student@example.com", password="hunter2pass"):
    return client.post(
        "/api/v1/students/register",
        json={"email": email, "password": password, "full_name": "Nguyen Van A"},
    )


def login(client, email="student@example.com", password="hunter2pass"):
    return client.post("/api/v1/students/login", json={"email": email, "password": password})


def test_register_creates_student(client):
    res = register(client)
    assert res.status_code == 201
    body = res.json()
    assert "password" not in body
    assert "password_hash" not in body
    assert body["email"] == "student@example.com"


def test_register_duplicate_email_rejected(client):
    register(client)
    res = register(client)
    assert res.status_code == 409
    assert res.json()["error"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_login_success_sets_cookies(client):
    register(client)
    res = login(client)
    assert res.status_code == 200
    assert settings.student_session_cookie_name in res.cookies
    assert settings.student_refresh_cookie_name in res.cookies


def test_login_wrong_password_rejected(client):
    register(client)
    res = login(client, password="wrong-password")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_login_third_device_rejected(client):
    register(client)
    res1 = login(client)
    res2 = login(client)
    assert res1.status_code == 200
    assert res2.status_code == 200
    res3 = login(client)
    assert res3.status_code == 409
    assert res3.json()["error"]["code"] == "DEVICE_LIMIT_EXCEEDED"


def test_logout_frees_device_slot(client):
    register(client)
    login(client)
    res2 = login(client)
    client.cookies.set(settings.student_refresh_cookie_name, res2.cookies[settings.student_refresh_cookie_name])
    logout_res = client.post("/api/v1/students/logout")
    assert logout_res.status_code == 200
    res3 = login(client)
    assert res3.status_code == 200
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_auth_v1.py -v`
Expected: FAIL — `ModuleNotFoundError` hoặc 404 (router chưa đăng ký)

- [ ] **Step 3: Implement repository**

```python
# backend/app/student_auth/repository.py
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.operational.database import SecurityStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_student(store: SecurityStore, *, email: str, password_hash: str, full_name: str | None, phone: str | None) -> str:
    existing = store.fetch_one("SELECT id FROM students WHERE email = ?", (email,))
    if existing is not None:
        raise ValueError("email_exists")
    student_id = f"stu_{uuid.uuid4().hex}"
    store.execute(
        "INSERT INTO students (id, email, password_hash, full_name, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (student_id, email, password_hash, full_name, phone, _utc_now_iso()),
    )
    return student_id


def find_student_by_email(store: SecurityStore, email: str) -> dict | None:
    row = store.fetch_one("SELECT * FROM students WHERE email = ?", (email,))
    return dict(row) if row else None


def count_active_sessions(store: SecurityStore, student_id: str) -> int:
    now = _utc_now_iso()
    row = store.fetch_one(
        "SELECT COUNT(*) AS n FROM student_sessions WHERE student_id = ? AND revoked_at IS NULL AND expires_at > ?",
        (student_id, now),
    )
    return int(row["n"]) if row else 0


def create_session(
    store: SecurityStore, *, student_id: str, refresh_token_hash: str, user_agent: str | None, ip_address: str | None, ttl_seconds: int
) -> str:
    session_id = f"sess_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
    store.execute(
        """
        INSERT INTO student_sessions
            (id, student_id, refresh_token_hash, user_agent, ip_address, created_at, last_seen_at, expires_at, revoked_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (session_id, student_id, refresh_token_hash, user_agent, ip_address, now.isoformat(), now.isoformat(), expires_at),
    )
    return session_id


def find_session_by_refresh_hash(store: SecurityStore, refresh_token_hash: str) -> dict | None:
    row = store.fetch_one(
        "SELECT * FROM student_sessions WHERE refresh_token_hash = ? AND revoked_at IS NULL",
        (refresh_token_hash,),
    )
    return dict(row) if row else None


def revoke_session(store: SecurityStore, session_id: str) -> None:
    store.execute(
        "UPDATE student_sessions SET revoked_at = ? WHERE id = ?",
        (_utc_now_iso(), session_id),
    )


def touch_session(store: SecurityStore, session_id: str) -> None:
    store.execute(
        "UPDATE student_sessions SET last_seen_at = ? WHERE id = ?",
        (_utc_now_iso(), session_id),
    )


def list_active_sessions(store: SecurityStore, student_id: str) -> list[dict]:
    now = _utc_now_iso()
    rows = store.fetch_all(
        """
        SELECT id, user_agent, ip_address, created_at, last_seen_at, expires_at
        FROM student_sessions
        WHERE student_id = ? AND revoked_at IS NULL AND expires_at > ?
        ORDER BY last_seen_at DESC
        """,
        (student_id, now),
    )
    return [dict(row) for row in rows]
```

- [ ] **Step 4: Implement router**

```python
# backend/app/api/student_auth_v1.py
from __future__ import annotations

import hashlib
import secrets

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.config import settings
from app.operational.database import get_store
from app.operational.errors import ERRORS
from app.student_auth import repository
from app.student_auth.passwords import hash_password, verify_password
from app.student_auth.tokens import create_student_access_token

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
    student = repository.find_student_by_email(store, "")  # placeholder replaced below
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
```

**Lưu ý khi implement Step 4:** dòng `student = repository.find_student_by_email(store, "")  # placeholder replaced below` là code thừa — xóa dòng đó, chỉ giữ dòng `row = store.fetch_one(...)` ngay sau. Sửa lại hàm `refresh` cho gọn:

```python
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
```

- [ ] **Step 5: Đăng ký router trong `main.py`**

Mở `backend/app/main.py`. Tìm dòng import router hiện có (dạng `from app.api import security_v1`), thêm ngay dưới:

```python
from app.api import student_auth_v1
```

Tìm dòng `app.include_router(security_v1.router, prefix="/api/v1/security", tags=["security-v1"])`, thêm ngay dưới:

```python
app.include_router(student_auth_v1.router, prefix="/api/v1/students", tags=["student-auth-v1"])
```

- [ ] **Step 6: Chạy test, xác nhận thành công**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_auth_v1.py -v`
Expected: PASS (6 tests)

- [ ] **Step 7: Chạy toàn bộ test suite backend để đảm bảo không phá vỡ gì**

Run: `cd backend && ./venv/bin/python -m pytest -q`
Expected: tất cả test pass (không có regression ở `test_phase4_operational_gateway.py` hay các test khác)

- [ ] **Step 8: Commit**

```bash
cd backend
git add app/student_auth/repository.py app/api/student_auth_v1.py app/main.py tests/test_student_auth_v1.py
git commit -m "feat(student-auth): add register/login/logout/refresh endpoints with 2-device limit"
```

---

## Task 7: Middleware `require_student` + endpoint devices + submissions

**Files:**
- Modify: `backend/app/api/student_auth_v1.py`
- Test: `backend/tests/test_student_devices.py`

**Interfaces:**
- Consumes: `verify_student_access_token` (Task 4), `repository.list_active_sessions/revoke_session` (Task 6)
- Produces: FastAPI dependency `require_student(request: Request) -> StudentTokenPayload`; endpoint `GET /api/v1/students/devices`, `POST /api/v1/students/devices/{session_id}/revoke`, `GET /api/v1/students/me`. Dùng bởi Task 9 (gắn `pseudonymous_user_id` vào `/analyze`) và frontend Task 10/11.

- [ ] **Step 1: Viết test thất bại**

```python
# backend/tests/test_student_devices.py
from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'student_devices_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield TestClient(app)
    settings.test_database_url = None


def register_and_login(client, email="student@example.com"):
    client.post("/api/v1/students/register", json={"email": email, "password": "hunter2pass", "full_name": "A"})
    return client.post("/api/v1/students/login", json={"email": email, "password": "hunter2pass"})


def test_devices_requires_auth(client):
    res = client.get("/api/v1/students/devices")
    assert res.status_code == 401


def test_devices_lists_active_sessions(client):
    login_res = register_and_login(client)
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])
    res = client.get("/api/v1/students/devices")
    assert res.status_code == 200
    body = res.json()
    assert len(body["devices"]) == 1
    assert "refresh_token_hash" not in body["devices"][0]


def test_me_returns_current_student(client):
    login_res = register_and_login(client)
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])
    res = client.get("/api/v1/students/me")
    assert res.status_code == 200
    assert res.json()["email"] == "student@example.com"
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_devices.py -v`
Expected: FAIL — 404 (endpoint chưa tồn tại)

- [ ] **Step 3: Thêm dependency `require_student` và 3 endpoint mới vào `student_auth_v1.py`**

Thêm import ở đầu file (`backend/app/api/student_auth_v1.py`), ngay dưới các import hiện có:

```python
from typing import Annotated

from fastapi import Depends, Header

from app.student_auth.tokens import StudentTokenPayload, verify_student_access_token
```

Thêm hàm dependency và 3 endpoint mới vào cuối file:

```python
def require_student(request: Request) -> StudentTokenPayload:
    token = request.cookies.get(settings.student_session_cookie_name)
    if not token:
        raise _StudentAuthError()
    try:
        return verify_student_access_token(token)
    except ValueError as exc:
        raise _StudentAuthError() from exc


class _StudentAuthError(Exception):
    pass


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
```

**Sửa lại `require_student`** để trả lỗi 401 chuẩn thay vì raise exception thô — dùng FastAPI exception handler. Thay khối `require_student`/`_StudentAuthError` ở trên bằng:

```python
from fastapi import HTTPException


def require_student(request: Request) -> StudentTokenPayload:
    token = request.cookies.get(settings.student_session_cookie_name)
    if not token:
        raise HTTPException(status_code=401, detail={"error": {"code": "UNAUTHORIZED", "message": "Login required."}})
    try:
        return verify_student_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail={"error": {"code": "UNAUTHORIZED", "message": "Session expired or invalid."}}) from exc
```

Xóa hẳn class `_StudentAuthError` (không cần nữa).

- [ ] **Step 4: Chạy test, xác nhận thành công**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_devices.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
cd backend
git add app/api/student_auth_v1.py tests/test_student_devices.py
git commit -m "feat(student-auth): add require_student middleware and device management endpoints"
```

---

## Task 8: Gắn `student_id` vào bài làm khi gọi `/analyze`

**Files:**
- Modify: `backend/app/api/student_auth_v1.py`
- Test: `backend/tests/test_student_submissions.py`

**Interfaces:**
- Produces: endpoint `GET /api/v1/students/submissions` — query `security_decisions` theo `pseudonymous_user_id = student.student_id`. Dùng bởi frontend Task 11 (lịch sử bài làm ở `/playground`).

**Ghi chú thiết kế:** Router `security_v1.py` không được sửa (ràng buộc spec). Việc gắn `pseudonymous_user_id = student_id` vào request `/analyze` là trách nhiệm của **frontend**: khi học viên đã đăng nhập, `student-api.ts` (Task 10) sẽ tự điền `pseudonymous_user_id` bằng `student_id` lấy từ `/api/v1/students/me` trước khi gọi `securityApi.analyze(...)`. Task này chỉ cần cung cấp endpoint đọc lại lịch sử.

- [ ] **Step 1: Viết test thất bại**

```python
# backend/tests/test_student_submissions.py
from __future__ import annotations

import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.auth import create_signed_token
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'student_submissions_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield TestClient(app)
    settings.test_database_url = None


def register_and_login(client, email="student@example.com"):
    client.post("/api/v1/students/register", json={"email": email, "password": "hunter2pass", "full_name": "A"})
    login_res = client.post("/api/v1/students/login", json={"email": email, "password": "hunter2pass"})
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])
    return client.get("/api/v1/students/me").json()["id"]


def submit_analysis(client, student_id: str):
    token = create_signed_token(subject="test-operator", roles=["viewer"], client_id="test-client")
    request_id = f"req-{uuid.uuid4().hex}"
    return client.post(
        "/api/v1/security/analyze",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "request_id": request_id,
            "submission_id": f"sub-{uuid.uuid4().hex}",
            "pseudonymous_user_id": student_id,
            "task_type": "writing",
            "candidate_content": "This is a clean practice essay about technology and education.",
        },
    )


def test_submissions_empty_for_new_student(client):
    student_id = register_and_login(client)
    res = client.get("/api/v1/students/submissions")
    assert res.status_code == 200
    assert res.json()["submissions"] == []


def test_submissions_lists_own_analysis(client):
    student_id = register_and_login(client)
    submit_analysis(client, student_id)
    res = client.get("/api/v1/students/submissions")
    assert res.status_code == 200
    submissions = res.json()["submissions"]
    assert len(submissions) == 1
    assert submissions[0]["applied_action"] is not None
```

- [ ] **Step 2: Chạy test, xác nhận thất bại**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_submissions.py -v`
Expected: FAIL — 404 (endpoint `/submissions` chưa tồn tại)

- [ ] **Step 3: Thêm endpoint `/submissions`**

Thêm vào cuối `backend/app/api/student_auth_v1.py`:

```python
@router.get("/submissions")
def list_submissions(student: Annotated[StudentTokenPayload, Depends(require_student)]):
    store = get_store()
    rows = store.fetch_all(
        """
        SELECT decision_id, request_id, applied_action, risk_score, severity, created_at
        FROM security_decisions
        WHERE pseudonymous_user_id = ?
        ORDER BY created_at DESC
        LIMIT 50
        """,
        (student.student_id,),
    )
    return {"submissions": [dict(row) for row in rows]}
```

**Lưu ý:** trước khi viết cứng tên cột, kiểm tra schema thật của `security_decisions`:

Run: `cd backend && ./venv/bin/python -c "
from app.config import settings
settings.test_database_url = 'sqlite:///:memory:'
from app.operational.database import reset_store_for_tests, get_store
reset_store_for_tests('sqlite:///:memory:')
store = get_store()
with store.connect() as con:
    print([r[1] for r in con.execute('PRAGMA table_info(security_decisions)').fetchall()])
"`

Nếu tên cột thực tế khác với `decision_id/request_id/applied_action/risk_score/severity/created_at` (ví dụ dùng `id` thay vì `decision_id`, hoặc không có cột `created_at`), sửa câu SQL trong endpoint `list_submissions` cho khớp đúng tên cột thật trước khi chạy lại test.

- [ ] **Step 4: Chạy test, xác nhận thành công**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_submissions.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Chạy toàn bộ test suite backend**

Run: `cd backend && ./venv/bin/python -m pytest -q`
Expected: tất cả pass, không regression

- [ ] **Step 6: Commit**

```bash
cd backend
git add app/api/student_auth_v1.py tests/test_student_submissions.py
git commit -m "feat(student-auth): add submissions history endpoint"
```

---

## Task 9: Frontend — `student-api.ts`

**Files:**
- Create: `frontend/src/lib/student-api.ts`

**Interfaces:**
- Consumes: `API_BASE` pattern từ `frontend/src/lib/security-api.ts` (dòng 158: `process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"`)
- Produces: `studentApi.register(input)`, `studentApi.login(input)`, `studentApi.logout()`, `studentApi.me()`, `studentApi.devices()`, `studentApi.revokeDevice(sessionId)`, `studentApi.submissions()` — Promise-based, dùng `credentials: "include"` để gửi httpOnly cookie. Dùng bởi Task 10, 11, 12.

- [ ] **Step 1: Viết `student-api.ts`**

```typescript
// frontend/src/lib/student-api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StudentApiError {
  code: string;
  message: string;
  retryable: boolean;
}

export class StudentRequestError extends Error {
  code: string;
  status: number;
  retryable: boolean;

  constructor(status: number, error: StudentApiError) {
    super(error.message);
    this.code = error.code;
    this.status = status;
    this.retryable = error.retryable;
  }
}

async function studentRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers ?? {}),
    },
  });
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    const error: StudentApiError = payload?.error ?? {
      code: "UNKNOWN_ERROR",
      message: "Something went wrong.",
      retryable: false,
    };
    throw new StudentRequestError(response.status, error);
  }
  return payload as T;
}

export interface StudentProfile {
  id: string;
  email: string;
  full_name?: string | null;
}

export interface StudentDevice {
  id: string;
  user_agent: string | null;
  ip_address: string | null;
  created_at: string;
  last_seen_at: string;
  expires_at: string;
}

export interface StudentSubmission {
  decision_id: string;
  request_id: string;
  applied_action: string;
  risk_score: number;
  severity: string;
  created_at: string;
}

export const studentApi = {
  register: (input: { email: string; password: string; full_name?: string; phone?: string }) =>
    studentRequest<StudentProfile>("/api/v1/students/register", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  login: (input: { email: string; password: string }) =>
    studentRequest<StudentProfile>("/api/v1/students/login", {
      method: "POST",
      body: JSON.stringify(input),
    }),

  logout: () => studentRequest<{ ok: boolean }>("/api/v1/students/logout", { method: "POST" }),

  me: () => studentRequest<StudentProfile>("/api/v1/students/me"),

  devices: () => studentRequest<{ devices: StudentDevice[] }>("/api/v1/students/devices"),

  revokeDevice: (sessionId: string) =>
    studentRequest<{ ok: boolean }>(`/api/v1/students/devices/${sessionId}/revoke`, { method: "POST" }),

  submissions: () => studentRequest<{ submissions: StudentSubmission[] }>("/api/v1/students/submissions"),
};
```

- [ ] **Step 2: Xác nhận file compile (TypeScript type-check)**

Run: `cd frontend && npx tsc --noEmit`
Expected: không có lỗi type trong `student-api.ts` (có thể có lỗi pre-existing ở file khác — chỉ cần xác nhận không thêm lỗi mới liên quan tới `student-api.ts`)

- [ ] **Step 3: Commit**

```bash
cd frontend
git add src/lib/student-api.ts
git commit -m "feat(student-auth): add frontend API client for student auth"
```

---

## Task 10: Frontend — trang `/register` và `/login`

**Files:**
- Create: `frontend/src/app/register/page.tsx`
- Create: `frontend/src/app/login/page.tsx`

**Interfaces:**
- Consumes: `studentApi.register`, `studentApi.login`, `StudentRequestError` (Task 9)
- Produces: route `/register`, `/login` hoạt động trên trình duyệt. Dùng bởi Task 12 (guard ở `/playground` redirect tới `/login`).

- [ ] **Step 1: Tạo trang đăng ký**

```tsx
// frontend/src/app/register/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { studentApi, StudentRequestError } from "@/lib/student-api";

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (password.length < 8) {
      setError("Mật khẩu phải có tối thiểu 8 ký tự.");
      return;
    }
    setSubmitting(true);
    try {
      await studentApi.register({ email, password, full_name: fullName || undefined });
      router.push("/login");
    } catch (err) {
      if (err instanceof StudentRequestError) {
        setError(err.message);
      } else {
        setError("Đăng ký thất bại, vui lòng thử lại.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold">Đăng ký tài khoản học viên</h1>
      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Họ tên
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Mật khẩu (tối thiểu 8 ký tự)
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-blue-600 px-4 py-2 font-semibold text-white disabled:opacity-50"
        >
          {submitting ? "Đang xử lý..." : "Đăng ký"}
        </button>
      </form>
    </main>
  );
}
```

- [ ] **Step 2: Tạo trang đăng nhập**

```tsx
// frontend/src/app/login/page.tsx
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { studentApi, StudentRequestError } from "@/lib/student-api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await studentApi.login({ email, password });
      router.push("/playground");
    } catch (err) {
      if (err instanceof StudentRequestError && err.code === "DEVICE_LIMIT_EXCEEDED") {
        setError("Bạn đã đăng nhập tối đa 2 thiết bị. Vui lòng đăng xuất một thiết bị khác trước.");
      } else if (err instanceof StudentRequestError) {
        setError(err.message);
      } else {
        setError("Đăng nhập thất bại, vui lòng thử lại.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="mx-auto max-w-sm px-4 py-16">
      <h1 className="text-2xl font-bold">Đăng nhập</h1>
      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-4">
        <label className="flex flex-col gap-1 text-sm">
          Email
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        <label className="flex flex-col gap-1 text-sm">
          Mật khẩu
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded border px-3 py-2"
          />
        </label>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-blue-600 px-4 py-2 font-semibold text-white disabled:opacity-50"
        >
          {submitting ? "Đang xử lý..." : "Đăng nhập"}
        </button>
      </form>
    </main>
  );
}
```

- [ ] **Step 3: Type-check**

Run: `cd frontend && npx tsc --noEmit`
Expected: không có lỗi mới liên quan `register/page.tsx`, `login/page.tsx`

- [ ] **Step 4: Commit**

```bash
cd frontend
git add src/app/register/page.tsx src/app/login/page.tsx
git commit -m "feat(student-auth): add register and login pages"
```

---

## Task 11: Frontend — trang `/account/devices`

**Files:**
- Create: `frontend/src/app/account/devices/page.tsx`

**Interfaces:**
- Consumes: `studentApi.devices`, `studentApi.revokeDevice`, `studentApi.me` (Task 9)

- [ ] **Step 1: Tạo trang quản lý thiết bị**

```tsx
// frontend/src/app/account/devices/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { studentApi, StudentDevice, StudentRequestError } from "@/lib/student-api";

export default function DevicesPage() {
  const router = useRouter();
  const [devices, setDevices] = useState<StudentDevice[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const res = await studentApi.devices();
      setDevices(res.devices);
    } catch (err) {
      if (err instanceof StudentRequestError && err.status === 401) {
        router.push("/login");
        return;
      }
      setError("Không tải được danh sách thiết bị.");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleRevoke(sessionId: string) {
    await studentApi.revokeDevice(sessionId);
    await load();
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-16">
      <h1 className="text-2xl font-bold">Thiết bị của tôi</h1>
      <p className="mt-2 text-sm text-gray-600">Bạn có thể đăng nhập tối đa 2 thiết bị cùng lúc.</p>
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      <ul className="mt-6 flex flex-col gap-3">
        {devices?.map((device) => (
          <li key={device.id} className="flex items-center justify-between rounded border px-4 py-3">
            <div>
              <p className="font-medium">{device.user_agent ?? "Thiết bị không xác định"}</p>
              <p className="text-xs text-gray-500">
                IP {device.ip_address ?? "?"} · Hoạt động lần cuối {new Date(device.last_seen_at).toLocaleString("vi-VN")}
              </p>
            </div>
            <button
              onClick={() => handleRevoke(device.id)}
              className="rounded border border-red-500 px-3 py-1 text-sm text-red-600 hover:bg-red-50"
            >
              Đăng xuất
            </button>
          </li>
        ))}
      </ul>
    </main>
  );
}
```

- [ ] **Step 2: Type-check**

Run: `cd frontend && npx tsc --noEmit`
Expected: không có lỗi mới liên quan `account/devices/page.tsx`

- [ ] **Step 3: Commit**

```bash
cd frontend
git add src/app/account/devices/page.tsx
git commit -m "feat(student-auth): add device management page"
```

---

## Task 12: Sửa `/playground` — yêu cầu đăng nhập, gắn student_id, hiển thị lịch sử

**Files:**
- Modify: `frontend/src/app/playground/page.tsx`
- Modify: `frontend/src/components/SecurityConsole.tsx` (chỉ đoạn liên quan tới build request `/analyze`, xem Interfaces bên dưới để biết đúng vị trí)

**Interfaces:**
- Consumes: `studentApi.me`, `studentApi.submissions` (Task 9); `SecurityConsolePage` component hiện có (không đổi chữ ký, chỉ thêm 1 prop tùy chọn)

**Lưu ý quan trọng:** `SecurityConsole.tsx` là file dùng chung cho nhiều trang (`view="playground"` và các view khác như benchmark, attack-arena). Task này **không được sửa logic chung của component** — chỉ thêm 1 khối UI "Lịch sử bài làm" hiển thị **riêng khi `view === "playground"` và có student đăng nhập**, và gắn `pseudonymous_user_id` vào request `/analyze` khi gọi từ Playground.

- [ ] **Step 1: Đọc đoạn code build request `/analyze` hiện tại để xác định vị trí sửa chính xác**

Run: `cd frontend && grep -n "pseudonymous_user_id\|candidate_content\|securityApi.analyze" src/components/SecurityConsole.tsx`

Ghi lại số dòng thực tế trả về — dùng số dòng đó thay cho vị trí ước lượng ở Step 3 bên dưới (agent khảo sát trước đó xác nhận `securityApi.analyze(session, request)` nằm ở khoảng dòng 723, nhưng phải xác nhận lại bằng grep vì file có thể đã đổi).

- [ ] **Step 2: Sửa `playground/page.tsx` để guard đăng nhập**

```tsx
// frontend/src/app/playground/page.tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { SecurityConsolePage } from "@/components/SecurityConsole";
import { studentApi, StudentProfile } from "@/lib/student-api";

export default function PlaygroundPage() {
  const router = useRouter();
  const [student, setStudent] = useState<StudentProfile | null>(null);
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    studentApi
      .me()
      .then((profile) => setStudent(profile))
      .catch(() => router.push("/login"))
      .finally(() => setChecked(true));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!checked) {
    return <main className="px-4 py-16 text-center text-sm text-gray-500">Đang kiểm tra đăng nhập...</main>;
  }
  if (!student) {
    return null;
  }

  return <SecurityConsolePage view="playground" studentId={student.id} />;
}
```

- [ ] **Step 3: Thêm prop `studentId` tùy chọn vào `SecurityConsolePage` và gắn vào request**

Mở `frontend/src/components/SecurityConsole.tsx`. Tìm định nghĩa props của `SecurityConsolePage` (tìm bằng `grep -n "SecurityConsolePage" src/components/SecurityConsole.tsx` để lấy đúng dòng khai báo interface/props). Thêm field tùy chọn:

```typescript
interface SecurityConsolePageProps {
  view: string; // giữ nguyên các field hiện có, chỉ thêm dòng dưới
  studentId?: string;
}
```

Tại vị trí xác định ở Step 1 (nơi build object `request` gửi cho `securityApi.analyze(session, request)`), sửa để điền `pseudonymous_user_id` khi có `studentId`:

```typescript
const request: GatewayRequest = {
  // ... giữ nguyên toàn bộ field hiện có ...
  pseudonymous_user_id: studentId ?? undefined,
};
```

**Không xóa hay đổi bất kỳ field nào khác đã có trong object `request`** — chỉ thêm/override field `pseudonymous_user_id`.

- [ ] **Step 4: Thêm khối "Lịch sử bài làm" chỉ hiện ở view playground**

Trong `SecurityConsolePage`, tìm phần JSX return chính (nơi render các card kết quả phân tích). Thêm 1 sub-component mới ngay trong cùng file, phía dưới component chính:

```tsx
function SubmissionHistory({ studentId }: { studentId: string }) {
  const [submissions, setSubmissions] = useState<StudentSubmission[]>([]);

  useEffect(() => {
    studentApi.submissions().then((res) => setSubmissions(res.submissions)).catch(() => setSubmissions([]));
  }, [studentId]);

  if (submissions.length === 0) return null;

  return (
    <section className="mt-8 rounded-2xl border p-6">
      <h2 className="text-lg font-semibold">Lịch sử bài làm của tôi</h2>
      <ul className="mt-4 flex flex-col gap-2">
        {submissions.map((s) => (
          <li key={s.decision_id} className="flex justify-between text-sm">
            <span>{new Date(s.created_at).toLocaleString("vi-VN")}</span>
            <span className="font-mono">{s.applied_action} · risk {Math.round(s.risk_score * 100)}%</span>
          </li>
        ))}
      </ul>
    </section>
  );
}
```

Thêm import cần thiết ở đầu file: `import { studentApi, StudentSubmission } from "@/lib/student-api";` (nếu `useState`/`useEffect` chưa được import trong file thì thêm vào dòng import React hooks hiện có, không tạo dòng import trùng lặp).

Trong JSX return của `SecurityConsolePage`, ngay trước thẻ đóng cuối cùng của phần nội dung chính (`</main>` hoặc tương đương — xác định bằng cách đọc cấu trúc JSX thật của file), thêm:

```tsx
{view === "playground" && studentId && <SubmissionHistory studentId={studentId} />}
```

- [ ] **Step 5: Type-check**

Run: `cd frontend && npx tsc --noEmit`
Expected: không có lỗi type mới trong `playground/page.tsx` hoặc `SecurityConsole.tsx`

- [ ] **Step 6: Kiểm thử thủ công trên trình duyệt**

Khởi động cả 2 server (nếu chưa chạy):
Run: `cd backend && ./venv/bin/python -m uvicorn app.main:app --port 8000 &`
Run: `cd frontend && npm run dev &`

Dùng Playwright (mcp__plugin_playwright_playwright__browser_navigate) điều hướng tới `http://localhost:3000/playground` khi chưa đăng nhập → xác nhận redirect sang `/login`. Đăng ký 1 tài khoản mới qua `/register`, đăng nhập, xác nhận vào lại được `/playground`, gửi 1 bài phân tích, xác nhận mục "Lịch sử bài làm của tôi" xuất hiện với đúng 1 dòng.

- [ ] **Step 7: Commit**

```bash
cd frontend
git add src/app/playground/page.tsx src/components/SecurityConsole.tsx
git commit -m "feat(student-auth): require login on playground and show submission history"
```

---

## Task 13: Header hiển thị học viên đăng nhập + đăng xuất

**Files:**
- Create: `frontend/src/components/StudentHeader.tsx`
- Modify: `frontend/src/app/playground/page.tsx`
- Modify: `frontend/src/app/account/devices/page.tsx`

**Interfaces:**
- Consumes: `studentApi.me`, `studentApi.logout` (Task 9)

- [ ] **Step 1: Tạo component header**

```tsx
// frontend/src/components/StudentHeader.tsx
"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { studentApi } from "@/lib/student-api";

export function StudentHeader({ email }: { email: string }) {
  const router = useRouter();

  async function handleLogout() {
    await studentApi.logout();
    router.push("/login");
  }

  return (
    <div className="flex items-center justify-between border-b px-4 py-3 text-sm">
      <span>{email}</span>
      <div className="flex items-center gap-4">
        <Link href="/account/devices" className="text-blue-600 hover:underline">
          Thiết bị của tôi
        </Link>
        <button onClick={handleLogout} className="text-red-600 hover:underline">
          Đăng xuất
        </button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Gắn header vào `/playground`**

Mở `frontend/src/app/playground/page.tsx` (đã sửa ở Task 12). Thêm import:

```tsx
import { StudentHeader } from "@/components/StudentHeader";
```

Sửa phần return khi đã có `student`, bọc thêm header phía trên `SecurityConsolePage`:

```tsx
return (
  <>
    <StudentHeader email={student.email} />
    <SecurityConsolePage view="playground" studentId={student.id} />
  </>
);
```

- [ ] **Step 3: Gắn header vào `/account/devices`**

Mở `frontend/src/app/account/devices/page.tsx`. Thêm state lấy profile và render header — thêm vào đầu component function, sau các `useState` hiện có:

```tsx
const [profile, setProfile] = useState<{ email: string } | null>(null);
```

Trong hàm `load()` hiện có, thêm gọi song song lấy profile (chỉnh sửa hàm `load` đã viết ở Task 11):

```tsx
async function load() {
  try {
    const [devicesRes, meRes] = await Promise.all([studentApi.devices(), studentApi.me()]);
    setDevices(devicesRes.devices);
    setProfile(meRes);
  } catch (err) {
    if (err instanceof StudentRequestError && err.status === 401) {
      router.push("/login");
      return;
    }
    setError("Không tải được danh sách thiết bị.");
  }
}
```

Thêm import `StudentHeader` và render trong JSX, ngay trước thẻ `<main>`:

```tsx
import { StudentHeader } from "@/components/StudentHeader";
```

```tsx
{profile && <StudentHeader email={profile.email} />}
<main className="mx-auto max-w-2xl px-4 py-16">
  {/* nội dung hiện có giữ nguyên */}
</main>
```

- [ ] **Step 4: Type-check**

Run: `cd frontend && npx tsc --noEmit`
Expected: không có lỗi type mới

- [ ] **Step 5: Kiểm thử thủ công**

Dùng Playwright điều hướng `/playground` sau khi đăng nhập → xác nhận header hiện đúng email và có link "Thiết bị của tôi" + nút "Đăng xuất". Bấm "Đăng xuất" → xác nhận redirect về `/login` và không thể truy cập lại `/playground` mà không đăng nhập lại.

- [ ] **Step 6: Commit**

```bash
cd frontend
git add src/components/StudentHeader.tsx src/app/playground/page.tsx src/app/account/devices/page.tsx
git commit -m "feat(student-auth): add student header with logout across authenticated pages"
```

---

## Task 14: Kiểm thử bảo mật — không lộ password/token qua log hoặc response

**Files:**
- Test: `backend/tests/test_student_auth_no_leak.py`

**Interfaces:**
- Consumes: toàn bộ router `student_auth_v1` (Task 6, 7)

- [ ] **Step 1: Viết test xác nhận không lộ dữ liệu nhạy cảm**

```python
# backend/tests/test_student_auth_no_leak.py
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'no_leak_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield TestClient(app)
    settings.test_database_url = None


def test_register_response_never_contains_password(client):
    res = client.post(
        "/api/v1/students/register",
        json={"email": "leak-test@example.com", "password": "super-secret-pass", "full_name": "A"},
    )
    body_text = res.text
    assert "super-secret-pass" not in body_text
    assert "password_hash" not in body_text


def test_login_response_never_contains_password_or_raw_refresh_token(client):
    client.post(
        "/api/v1/students/register",
        json={"email": "leak-test2@example.com", "password": "super-secret-pass", "full_name": "A"},
    )
    res = client.post(
        "/api/v1/students/login", json={"email": "leak-test2@example.com", "password": "super-secret-pass"}
    )
    body_text = res.text
    assert "super-secret-pass" not in body_text
    assert "password_hash" not in body_text
    refresh_cookie_value = res.cookies.get(settings.student_refresh_cookie_name)
    assert refresh_cookie_value is not None
    assert refresh_cookie_value not in body_text


def test_stored_refresh_token_is_hashed_not_plaintext(client):
    client.post(
        "/api/v1/students/register",
        json={"email": "leak-test3@example.com", "password": "super-secret-pass", "full_name": "A"},
    )
    res = client.post(
        "/api/v1/students/login", json={"email": "leak-test3@example.com", "password": "super-secret-pass"}
    )
    raw_refresh = res.cookies[settings.student_refresh_cookie_name]
    store = get_store()
    row = store.fetch_one("SELECT refresh_token_hash FROM student_sessions LIMIT 1")
    assert row["refresh_token_hash"] != raw_refresh
    assert len(row["refresh_token_hash"]) == 64  # sha256 hex digest
```

- [ ] **Step 2: Chạy test**

Run: `cd backend && ./venv/bin/python -m pytest tests/test_student_auth_no_leak.py -v`
Expected: PASS (3 tests). Nếu FAIL, đây là bug thật trong Task 6 (ví dụ response model vô tình include field nhạy cảm) — sửa lại router trước khi tiếp tục, không nới lỏng test.

- [ ] **Step 3: Chạy toàn bộ test suite backend lần cuối**

Run: `cd backend && ./venv/bin/python -m pytest -q`
Expected: tất cả pass

- [ ] **Step 4: Commit**

```bash
cd backend
git add tests/test_student_auth_no_leak.py
git commit -m "test(student-auth): verify no password or raw token leakage"
```

---

## Task 15: Cập nhật `.env.example` và README

**Files:**
- Modify: `backend/.env.example`
- Modify: `README.md`

**Interfaces:** (none — tài liệu)

- [ ] **Step 1: Thêm biến môi trường mới vào `.env.example`**

Mở `backend/.env.example`, thêm vào cuối file:

```
# Student account auth (separate from operator console auth above)
STUDENT_TOKEN_SECRET=student-development-only-change-me
STUDENT_ACCESS_TOKEN_TTL_SECONDS=1800
STUDENT_REFRESH_TOKEN_TTL_SECONDS=604800
STUDENT_MAX_DEVICES=2
```

- [ ] **Step 2: Cập nhật README.md mục "Product Pages" và "API Overview"**

Thêm vào danh sách "Product Pages" trong `README.md` (tìm mục `## 7. Product Pages`):

```
- **`/register`**: Đăng ký tài khoản học viên.
- **`/login`**: Đăng nhập học viên (email + mật khẩu, tối đa 2 thiết bị).
- **`/account/devices`**: Quản lý thiết bị đang đăng nhập.
```

Thêm vào mục "API Overview" (tìm mục `## 11. API Overview`):

```
- `POST /api/v1/students/register`: Đăng ký tài khoản học viên mới.
- `POST /api/v1/students/login`: Đăng nhập, từ chối nếu đã đủ 2 thiết bị.
- `GET /api/v1/students/devices`: Liệt kê thiết bị đang đăng nhập.
```

- [ ] **Step 3: Commit**

```bash
git add backend/.env.example README.md
git commit -m "docs: document student auth env vars and new routes"
```

---

## Self-review notes (đã kiểm tra trước khi bàn giao)

- **Spec coverage**: mọi mục trong spec (`2026-07-17-student-account-security-design.md`) đều có task tương ứng — schema (Task 1), password hashing (Task 2), token (Task 4), 7 API endpoints (Task 6, 7, 8), 3 trang frontend (Task 10, 11), sửa Playground (Task 12), header (Task 13), kiểm thử không lộ dữ liệu (Task 14).
- **Ngoài phạm vi đã tôn trọng**: không có task nào đụng `operational/auth.py`/`security_v1.py`/firewall; không mã hóa PII at-rest; không device fingerprinting; không reset password qua email.
- **Type consistency đã rà**: `StudentTokenPayload` (Task 4) dùng nhất quán ở Task 7/8; `studentApi` object (Task 9) dùng nhất quán ở Task 10/11/12/13; tên cookie `settings.student_session_cookie_name`/`student_refresh_cookie_name` (Task 3) dùng nhất quán xuyên suốt Task 6/7/14.
- **Rủi ro cần lưu ý khi thực thi**: Task 8 và Task 12 có bước "xác nhận tên cột/vị trí dòng thật trong code trước khi viết cứng" — vì agent khảo sát trước đó không đọc toàn bộ `security_v1.py`/`SecurityConsole.tsx`, nên implementer phải tự grep xác nhận trước khi áp code mẫu, tránh sai lệch tên cột/dòng.
