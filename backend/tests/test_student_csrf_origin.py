from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'csrf_origin_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    client = TestClient(app)
    client.headers.update({"origin": "http://localhost:3000"})
    yield client
    settings.test_database_url = None


def register(client, email="csrf@example.com"):
    return client.post(
        "/api/v1/students/register",
        json={"email": email, "password": "hunter2pass", "full_name": "A"},
    )


def test_login_rejected_from_untrusted_origin(client):
    register(client)
    client.headers.update({"origin": "https://evil.example.com"})
    res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ORIGIN_NOT_TRUSTED"


def test_login_rejected_with_no_origin_or_referer(client):
    register(client)
    client.headers.pop("origin", None)
    res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ORIGIN_NOT_TRUSTED"


def test_login_accepted_from_trusted_origin(client):
    register(client)
    res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    assert res.status_code == 200


def test_login_accepted_via_referer_fallback_when_origin_missing(client):
    register(client)
    client.headers.pop("origin", None)
    client.headers.update({"referer": "http://localhost:3000/login"})
    res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    assert res.status_code == 200


def test_logout_rejected_from_untrusted_origin(client):
    register(client)
    login_res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    client.headers.update({"origin": "https://evil.example.com"})
    res = client.post("/api/v1/students/logout")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ORIGIN_NOT_TRUSTED"


def test_refresh_rejected_from_untrusted_origin(client):
    register(client)
    login_res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    client.cookies.set(settings.student_refresh_cookie_name, login_res.cookies[settings.student_refresh_cookie_name])
    client.headers.update({"origin": "https://evil.example.com"})
    res = client.post("/api/v1/students/refresh")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ORIGIN_NOT_TRUSTED"


def test_revoke_device_rejected_from_untrusted_origin(client):
    register(client)
    login_res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])
    devices_res = client.get("/api/v1/students/devices")
    session_id = devices_res.json()["devices"][0]["id"]

    client.headers.update({"origin": "https://evil.example.com"})
    res = client.post(f"/api/v1/students/devices/{session_id}/revoke")
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ORIGIN_NOT_TRUSTED"


def test_analyze_rejected_from_untrusted_origin(client):
    register(client)
    login_res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])

    client.headers.update({"origin": "https://evil.example.com"})
    res = client.post(
        "/api/v1/students/analyze",
        json={"submission_id": "sub-1", "task_type": "writing", "candidate_content": "hello"},
    )
    assert res.status_code == 403
    assert res.json()["error"]["code"] == "ORIGIN_NOT_TRUSTED"


def test_get_endpoints_do_not_require_origin_check(client):
    """GET endpoints are read-only and not state-changing, so they are
    intentionally not gated by require_trusted_origin -- a cross-site GET
    already can't be prevented by SameSite=Lax expectations the same way,
    and reading data (without cookies being attacker-controlled) is not the
    CSRF threat model this defends against. Confirm they still work from an
    origin that would be rejected on a POST route."""
    register(client)
    login_res = client.post("/api/v1/students/login", json={"email": "csrf@example.com", "password": "hunter2pass"})
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])

    client.headers.update({"origin": "https://evil.example.com"})
    res = client.get("/api/v1/students/me")
    assert res.status_code == 200
