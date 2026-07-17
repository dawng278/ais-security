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
    client = TestClient(app)
    client.headers.update({"origin": "http://localhost:3000"})
    yield client
    settings.test_database_url = None


def register_and_login(client, email="student@example.com"):
    client.post("/api/v1/students/register", json={"email": email, "password": "hunter2pass", "full_name": "A"})
    return client.post("/api/v1/students/login", json={"email": email, "password": "hunter2pass"})


def test_devices_requires_auth(client):
    res = client.get("/api/v1/students/devices")
    assert res.status_code == 401


def test_devices_requires_auth_returns_consistent_error_shape(client):
    res = client.get("/api/v1/students/devices")
    assert res.status_code == 401
    body = res.json()
    assert "detail" not in body
    assert body == {
        "error": {
            "code": "UNAUTHORIZED",
            "message": "Authentication is required.",
            "retryable": False,
            "correlation_id": None,
        }
    }


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


def test_revoke_device_succeeds_for_own_session(client):
    login_res = register_and_login(client)
    client.cookies.set(settings.student_session_cookie_name, login_res.cookies[settings.student_session_cookie_name])
    devices = client.get("/api/v1/students/devices").json()["devices"]
    session_id = devices[0]["id"]

    res = client.post(f"/api/v1/students/devices/{session_id}/revoke")
    assert res.status_code == 200
    assert res.json()["ok"] is True

    remaining = client.get("/api/v1/students/devices").json()["devices"]
    assert all(d["id"] != session_id for d in remaining)


def test_revoke_device_rejects_other_students_session(client):
    login_res_a = register_and_login(client, email="a@example.com")
    login_res_b = register_and_login(client, email="b@example.com")

    # Student A's session id, obtained while authenticated as A.
    client.cookies.set(settings.student_session_cookie_name, login_res_a.cookies[settings.student_session_cookie_name])
    devices_a = client.get("/api/v1/students/devices").json()["devices"]
    session_id_a = devices_a[0]["id"]

    # Switch to student B and attempt to revoke A's session.
    client.cookies.set(settings.student_session_cookie_name, login_res_b.cookies[settings.student_session_cookie_name])
    res = client.post(f"/api/v1/students/devices/{session_id_a}/revoke")
    assert res.status_code != 200

    # Confirm A's session is still active.
    client.cookies.set(settings.student_session_cookie_name, login_res_a.cookies[settings.student_session_cookie_name])
    devices_a_after = client.get("/api/v1/students/devices").json()["devices"]
    assert any(d["id"] == session_id_a for d in devices_a_after)


def test_devices_requires_auth_rejects_invalid_cookie(client):
    client.cookies.set(settings.student_session_cookie_name, "not-a-valid-token")
    res = client.get("/api/v1/students/devices")
    assert res.status_code == 401
