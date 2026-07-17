from __future__ import annotations

from app.student_auth.passwords import hash_password, verify_password


def test_hash_password_produces_different_output_than_input():
    hashed = hash_password("correct-horse-battery-staple")
    assert hashed != "correct-horse-battery-staple"
    assert len(hashed) > 20


def test_verify_password_accepts_correct_password():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("wrong-password", hashed) is False


def test_hash_password_is_salted():
    a = hash_password("same-password")
    b = hash_password("same-password")
    assert a != b
