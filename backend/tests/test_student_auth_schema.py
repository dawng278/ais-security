from __future__ import annotations

from pathlib import Path

import pytest

from app.config import settings
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests


@pytest.fixture()
def store(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'schema_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    yield get_store()
    settings.test_database_url = None


def test_students_table_exists(store):
    with store.connect() as con:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='students'"
        ).fetchone()
    assert row is not None


def test_student_sessions_table_exists(store):
    with store.connect() as con:
        row = con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='student_sessions'"
        ).fetchone()
    assert row is not None


def test_student_sessions_has_expected_columns(store):
    with store.connect() as con:
        cols = {r[1] for r in con.execute("PRAGMA table_info(student_sessions)").fetchall()}
    assert cols == {
        "id",
        "student_id",
        "refresh_token_hash",
        "user_agent",
        "ip_address",
        "created_at",
        "last_seen_at",
        "expires_at",
        "revoked_at",
    }
