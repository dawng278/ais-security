from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'cookie_security_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    client = TestClient(app)
    client.headers.update({"origin": "http://localhost:3000"})
    yield client
    settings.test_database_url = None


def register_and_login(client, email="cookie@example.com"):
    client.post("/api/v1/students/register", json={"email": email, "password": "hunter2pass", "full_name": "A"})
    return client.post("/api/v1/students/login", json={"email": email, "password": "hunter2pass"})


def _cookie_header_for(res, cookie_name: str) -> str:
    headers = res.headers.get_list("set-cookie")
    matches = [h for h in headers if h.startswith(f"{cookie_name}=")]
    assert matches, f"no Set-Cookie header found for {cookie_name}"
    return matches[0]


def test_cookies_not_secure_in_development(client):
    assert settings.env != "production"
    res = register_and_login(client)
    access_header = _cookie_header_for(res, settings.student_session_cookie_name)
    refresh_header = _cookie_header_for(res, settings.student_refresh_cookie_name)
    assert "Secure" not in access_header
    assert "Secure" not in refresh_header


def test_cookies_are_secure_in_production(client):
    original_env = settings.env
    settings.env = "production"
    try:
        res = register_and_login(client, email="prod@example.com")
        access_header = _cookie_header_for(res, settings.student_session_cookie_name)
        refresh_header = _cookie_header_for(res, settings.student_refresh_cookie_name)
        assert "Secure" in access_header
        assert "Secure" in refresh_header
    finally:
        settings.env = original_env


def test_cookies_are_httponly_and_scoped_to_root_path(client):
    res = register_and_login(client)
    access_header = _cookie_header_for(res, settings.student_session_cookie_name)
    refresh_header = _cookie_header_for(res, settings.student_refresh_cookie_name)
    assert "HttpOnly" in access_header
    assert "HttpOnly" in refresh_header
    assert "Path=/" in access_header
    assert "Path=/" in refresh_header


def test_refresh_cookie_also_secure_in_production(client):
    login_res = register_and_login(client, email="prod2@example.com")
    original_env = settings.env
    settings.env = "production"
    try:
        client.cookies.set(settings.student_refresh_cookie_name, login_res.cookies[settings.student_refresh_cookie_name])
        refresh_res = client.post("/api/v1/students/refresh")
        access_header = _cookie_header_for(refresh_res, settings.student_session_cookie_name)
        assert "Secure" in access_header
    finally:
        settings.env = original_env
