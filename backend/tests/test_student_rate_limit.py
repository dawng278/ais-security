from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'rate_limit_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    original_email_limit = settings.student_login_max_attempts_per_email
    original_ip_limit = settings.student_login_max_attempts_per_ip
    original_register_limit = settings.student_register_max_attempts_per_ip
    client = TestClient(app)
    client.headers.update({"origin": "http://localhost:3000"})
    yield client
    settings.test_database_url = None
    settings.student_login_max_attempts_per_email = original_email_limit
    settings.student_login_max_attempts_per_ip = original_ip_limit
    settings.student_register_max_attempts_per_ip = original_register_limit


def register(client, email="ratelimit@example.com"):
    return client.post(
        "/api/v1/students/register",
        json={"email": email, "password": "hunter2pass", "full_name": "A"},
    )


def test_login_blocked_after_too_many_wrong_password_attempts_for_same_email(client):
    settings.student_login_max_attempts_per_email = 3
    register(client)
    for _ in range(3):
        res = client.post("/api/v1/students/login", json={"email": "ratelimit@example.com", "password": "wrong"})
        assert res.status_code == 401

    res = client.post("/api/v1/students/login", json={"email": "ratelimit@example.com", "password": "wrong"})
    assert res.status_code == 429
    assert res.json()["error"]["code"] == "RATE_LIMITED"


def test_login_blocked_after_too_many_attempts_still_blocks_correct_password(client):
    """Rate limiting must apply before credential verification -- otherwise
    an attacker who eventually guesses correctly on the Nth attempt bypasses
    the throttle entirely."""
    settings.student_login_max_attempts_per_email = 2
    register(client)
    for _ in range(2):
        client.post("/api/v1/students/login", json={"email": "ratelimit@example.com", "password": "wrong"})

    res = client.post("/api/v1/students/login", json={"email": "ratelimit@example.com", "password": "hunter2pass"})
    assert res.status_code == 429


def test_login_rate_limit_is_per_email_not_global(client):
    settings.student_login_max_attempts_per_email = 2
    settings.student_login_max_attempts_per_ip = 100
    register(client, email="a@example.com")
    register(client, email="b@example.com")

    for _ in range(2):
        client.post("/api/v1/students/login", json={"email": "a@example.com", "password": "wrong"})
    blocked_res = client.post("/api/v1/students/login", json={"email": "a@example.com", "password": "wrong"})
    assert blocked_res.status_code == 429

    still_ok_res = client.post("/api/v1/students/login", json={"email": "b@example.com", "password": "wrong"})
    assert still_ok_res.status_code == 401


def test_login_blocked_by_ip_limit_across_different_emails(client):
    settings.student_login_max_attempts_per_ip = 3
    settings.student_login_max_attempts_per_email = 100
    register(client, email="c@example.com")
    register(client, email="d@example.com")

    client.post("/api/v1/students/login", json={"email": "c@example.com", "password": "wrong"})
    client.post("/api/v1/students/login", json={"email": "c@example.com", "password": "wrong"})
    client.post("/api/v1/students/login", json={"email": "d@example.com", "password": "wrong"})

    res = client.post("/api/v1/students/login", json={"email": "d@example.com", "password": "wrong"})
    assert res.status_code == 429


def test_register_blocked_after_too_many_attempts_from_same_ip(client):
    settings.student_register_max_attempts_per_ip = 2
    register(client, email="reg1@example.com")
    register(client, email="reg2@example.com")

    res = register(client, email="reg3@example.com")
    assert res.status_code == 429
    assert res.json()["error"]["code"] == "RATE_LIMITED"
