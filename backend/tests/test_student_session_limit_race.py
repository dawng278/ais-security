from __future__ import annotations

import threading
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.operational.database import assert_isolated_test_database, get_store, reset_store_for_tests
from app.student_auth import repository
from app.student_auth.passwords import hash_password


@pytest.fixture()
def client(tmp_path: Path):
    db_url = f"sqlite:///{tmp_path / 'session_race_test.db'}"
    settings.test_database_url = db_url
    assert_isolated_test_database(db_url)
    reset_store_for_tests(db_url)
    client = TestClient(app)
    client.headers.update({"origin": "http://localhost:3000"})
    yield client
    settings.test_database_url = None


def test_concurrent_logins_never_exceed_device_limit(client):
    """Regression test for a race condition where login() previously checked
    count_active_sessions() and called create_session() as two separate,
    unsynchronized database calls: two concurrent logins could both read a
    count below the limit and both insert, exceeding student_max_devices.

    This fires many concurrent login requests (well above the limit) and
    asserts the final active-session count never exceeds the configured
    limit, regardless of how many succeeded."""
    client.post(
        "/api/v1/students/register",
        json={"email": "race@example.com", "password": "hunter2pass", "full_name": "Race"},
    )

    n_threads = 15
    barrier = threading.Barrier(n_threads)
    results: list[int] = []
    lock = threading.Lock()

    def do_login():
        c = TestClient(app)
        c.headers.update({"origin": "http://localhost:3000"})
        barrier.wait()
        res = c.post("/api/v1/students/login", json={"email": "race@example.com", "password": "hunter2pass"})
        with lock:
            results.append(res.status_code)

    threads = [threading.Thread(target=do_login) for _ in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    accepted = results.count(200)
    assert accepted <= settings.student_max_devices, (
        f"{accepted} concurrent logins were accepted, exceeding the device limit of "
        f"{settings.student_max_devices}: {sorted(results)}"
    )

    store = get_store()
    final_count = repository.count_active_sessions(store, _find_student_id(store, "race@example.com"))
    assert final_count <= settings.student_max_devices, (
        f"final active session count {final_count} exceeds limit {settings.student_max_devices}"
    )


def test_direct_interleaving_cannot_exceed_limit(client):
    """Directly proves the atomicity property at the repository layer: two
    "requests" that both observe the pre-insert session count (the exact
    interleaving a real race produces) must not both be allowed to create a
    session once the limit is reached. With try_create_session_within_limit,
    each call re-checks the count inside its own transaction, so a stale
    count read by a *previous* Python-level variable cannot bypass the gate
    the way the old two-call pattern did."""
    store = get_store()
    student_id = repository.create_student(
        store, email="direct@example.com", password_hash=hash_password("hunter2pass"), full_name="Direct", phone=None
    )

    first = repository.try_create_session_within_limit(
        store, student_id=student_id, refresh_token_hash="hash-a", user_agent="A", ip_address="1.1.1.1",
        ttl_seconds=604800, max_devices=settings.student_max_devices,
    )
    second = repository.try_create_session_within_limit(
        store, student_id=student_id, refresh_token_hash="hash-b", user_agent="B", ip_address="2.2.2.2",
        ttl_seconds=604800, max_devices=settings.student_max_devices,
    )
    third = repository.try_create_session_within_limit(
        store, student_id=student_id, refresh_token_hash="hash-c", user_agent="C", ip_address="3.3.3.3",
        ttl_seconds=604800, max_devices=settings.student_max_devices,
    )

    assert first is not None
    assert second is not None
    assert third is None, "third session should be rejected once the limit is reached"

    final_count = repository.count_active_sessions(store, student_id)
    assert final_count == settings.student_max_devices


def _find_student_id(store, email: str) -> str:
    student = repository.find_student_by_email(store, email)
    assert student is not None
    return student["id"]
