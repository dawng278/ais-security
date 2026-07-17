from __future__ import annotations

import time

import pytest

from app.student_auth.tokens import create_student_access_token, verify_student_access_token


def test_create_and_verify_roundtrip():
    token = create_student_access_token(student_id="stu-1", email="a@example.com", session_id="sess-1")
    payload = verify_student_access_token(token)
    assert payload.student_id == "stu-1"
    assert payload.email == "a@example.com"
    assert payload.session_id == "sess-1"


def test_verify_rejects_tampered_token():
    token = create_student_access_token(student_id="stu-1", email="a@example.com", session_id="sess-1")
    tampered = token[:-4] + "abcd"
    with pytest.raises(ValueError):
        verify_student_access_token(tampered)


def test_verify_rejects_expired_token():
    token = create_student_access_token(student_id="stu-1", email="a@example.com", session_id="sess-1", ttl_seconds=-1)
    with pytest.raises(ValueError):
        verify_student_access_token(token)


def test_verify_rejects_malformed_token():
    with pytest.raises(ValueError):
        verify_student_access_token("not-a-valid-token")
