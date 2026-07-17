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
    db_url = f"sqlite:///{tmp_path / 'no_leak_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    client = TestClient(app)
    client.headers.update({"origin": "http://localhost:3000"})
    yield client
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
    assert row["refresh_token_hash"] == hashlib.sha256(raw_refresh.encode("utf-8")).hexdigest()
