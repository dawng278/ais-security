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
    token = create_signed_token(subject="test-operator", roles=["integration_service"], client_id="test-client")
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


def test_submissions_requires_authentication(client):
    res = client.get("/api/v1/students/submissions")
    assert res.status_code == 401


def test_submissions_empty_for_new_student(client):
    register_and_login(client)
    res = client.get("/api/v1/students/submissions")
    assert res.status_code == 200
    assert res.json()["submissions"] == []


def test_submissions_lists_own_analysis(client):
    student_id = register_and_login(client)
    analyze_res = submit_analysis(client, student_id)
    assert analyze_res.status_code == 200
    res = client.get("/api/v1/students/submissions")
    assert res.status_code == 200
    submissions = res.json()["submissions"]
    assert len(submissions) == 1
    assert submissions[0]["selected_action"] is not None
    assert submissions[0]["request_id"] is not None
    assert submissions[0]["decision_id"] is not None


def test_submissions_does_not_leak_other_students(client):
    student_a_id = register_and_login(client, email="alice@example.com")
    submit_analysis(client, student_a_id)

    # Switch session to a second student who has no submissions of their own.
    client.cookies.clear()
    register_and_login(client, email="bob@example.com")
    res = client.get("/api/v1/students/submissions")
    assert res.status_code == 200
    assert res.json()["submissions"] == []
