from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'student_analyze_test.db'}"
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


def analyze_payload(**overrides):
    payload = {
        "submission_id": "sub-001",
        "task_type": "writing",
        "candidate_content": "This is a clean practice essay about technology and education.",
    }
    payload.update(overrides)
    return payload


def test_analyze_requires_authentication(client):
    res = client.post("/api/v1/students/analyze", json=analyze_payload())
    assert res.status_code == 401


def test_analyze_binds_submission_to_authenticated_student(client):
    student_id = register_and_login(client)
    res = client.post("/api/v1/students/analyze", json=analyze_payload())
    assert res.status_code == 200

    store = get_store()
    row = store.fetch_one(
        "SELECT pseudonymous_user_id FROM security_decisions WHERE request_id = ?",
        (res.json()["request_id"],),
    )
    assert row is not None
    assert row["pseudonymous_user_id"] == student_id


def test_analyze_rejects_client_supplied_student_id_field(client):
    """The request schema must not even accept a student-controlled identity
    field -- this is the core fix: a malicious client cannot pass
    pseudonymous_user_id (or student_id) to attribute a submission to
    another student, because the field does not exist on the student-facing
    schema at all (extra="forbid" rejects the whole request)."""
    register_and_login(client)
    res = client.post(
        "/api/v1/students/analyze",
        json=analyze_payload(pseudonymous_user_id="stu_someone_else"),
    )
    assert res.status_code == 422


def test_analyze_rejects_client_supplied_student_id_alias_field(client):
    register_and_login(client)
    res = client.post(
        "/api/v1/students/analyze",
        json=analyze_payload(student_id="stu_someone_else"),
    )
    assert res.status_code == 422


def test_student_a_cannot_attribute_submission_to_student_b(client):
    """End-to-end proof: even if student A tries every available request
    field to impersonate student B, the resulting submission is recorded
    under A's own authenticated identity, and never appears in B's history."""
    student_a_id = register_and_login(client, email="alice@example.com")
    res = client.post("/api/v1/students/analyze", json=analyze_payload())
    assert res.status_code == 200

    store = get_store()
    row = store.fetch_one(
        "SELECT pseudonymous_user_id FROM security_decisions WHERE request_id = ?",
        (res.json()["request_id"],),
    )
    assert row["pseudonymous_user_id"] == student_a_id

    client.cookies.clear()
    register_and_login(client, email="bob@example.com")
    submissions_res = client.get("/api/v1/students/submissions")
    assert submissions_res.json()["submissions"] == []


def test_analyze_response_appears_in_own_submission_history(client):
    register_and_login(client)
    analyze_res = client.post("/api/v1/students/analyze", json=analyze_payload())
    assert analyze_res.status_code == 200

    history_res = client.get("/api/v1/students/submissions")
    submissions = history_res.json()["submissions"]
    assert len(submissions) == 1
    assert submissions[0]["request_id"] == analyze_res.json()["request_id"]
