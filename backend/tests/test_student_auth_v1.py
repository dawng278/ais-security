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
