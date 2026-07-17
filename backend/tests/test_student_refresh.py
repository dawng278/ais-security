from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'student_refresh_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield TestClient(app)
    settings.test_database_url = None


def register_and_login(client, email="refresh@example.com", password="hunter2pass"):
    client.post(
        "/api/v1/students/register",
        json={"email": email, "password": password, "full_name": "Refresh Tester"},
    )
    return client.post("/api/v1/students/login", json={"email": email, "password": password})


def test_refresh_with_no_cookie_rejected(client):
    res = client.post("/api/v1/students/refresh")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_refresh_reissues_access_cookie(client):
    login_res = register_and_login(client)
    client.cookies.set(settings.student_refresh_cookie_name, login_res.cookies[settings.student_refresh_cookie_name])
    res = client.post("/api/v1/students/refresh")
    assert res.status_code == 200
    assert res.json() == {"ok": True}
    assert settings.student_session_cookie_name in res.cookies


def test_refresh_after_revoke_rejected(client):
    login_res = register_and_login(client)
    raw_refresh = login_res.cookies[settings.student_refresh_cookie_name]
    client.cookies.set(settings.student_refresh_cookie_name, raw_refresh)
    client.post("/api/v1/students/logout")

    client.cookies.set(settings.student_refresh_cookie_name, raw_refresh)
    res = client.post("/api/v1/students/refresh")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_refresh_with_expired_unrevoked_session_rejected(client):
    """Regression test: find_session_by_refresh_hash previously omitted
    expires_at from its WHERE clause, so an expired-but-unrevoked refresh
    session could still mint a fresh access token indefinitely."""
    login_res = register_and_login(client)
    raw_refresh = login_res.cookies[settings.student_refresh_cookie_name]

    store = get_store()
    refresh_hash = hashlib.sha256(raw_refresh.encode("utf-8")).hexdigest()
    # Force the session's expires_at into the past directly via SQL, simulating
    # a refresh token that has outlived its TTL but was never revoked.
    store.execute(
        "UPDATE student_sessions SET expires_at = '2000-01-01T00:00:00+00:00' WHERE refresh_token_hash = ?",
        (refresh_hash,),
    )

    client.cookies.set(settings.student_refresh_cookie_name, raw_refresh)
    res = client.post("/api/v1/students/refresh")
    assert res.status_code == 401
    assert res.json()["error"]["code"] == "INVALID_CREDENTIALS"
