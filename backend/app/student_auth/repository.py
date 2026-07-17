from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from app.operational.database import SecurityStore


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_student(store: SecurityStore, *, email: str, password_hash: str, full_name: str | None, phone: str | None) -> str:
    existing = store.fetch_one("SELECT id FROM students WHERE email = ?", (email,))
    if existing is not None:
        raise ValueError("email_exists")
    student_id = f"stu_{uuid.uuid4().hex}"
    store.execute(
        "INSERT INTO students (id, email, password_hash, full_name, phone, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (student_id, email, password_hash, full_name, phone, _utc_now_iso()),
    )
    return student_id


def find_student_by_email(store: SecurityStore, email: str) -> dict | None:
    row = store.fetch_one("SELECT * FROM students WHERE email = ?", (email,))
    return dict(row) if row else None


def count_active_sessions(store: SecurityStore, student_id: str) -> int:
    now = _utc_now_iso()
    row = store.fetch_one(
        "SELECT COUNT(*) AS n FROM student_sessions WHERE student_id = ? AND revoked_at IS NULL AND expires_at > ?",
        (student_id, now),
    )
    return int(row["n"]) if row else 0


def create_session(
    store: SecurityStore, *, student_id: str, refresh_token_hash: str, user_agent: str | None, ip_address: str | None, ttl_seconds: int
) -> str:
    session_id = f"sess_{uuid.uuid4().hex}"
    now = datetime.now(timezone.utc)
    expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
    store.execute(
        """
        INSERT INTO student_sessions
            (id, student_id, refresh_token_hash, user_agent, ip_address, created_at, last_seen_at, expires_at, revoked_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (session_id, student_id, refresh_token_hash, user_agent, ip_address, now.isoformat(), now.isoformat(), expires_at),
    )
    return session_id


def try_create_session_within_limit(
    store: SecurityStore,
    *,
    student_id: str,
    refresh_token_hash: str,
    user_agent: str | None,
    ip_address: str | None,
    ttl_seconds: int,
    max_devices: int,
) -> str | None:
    """Atomically check the active-session count and insert a new session in a
    single transaction, so two concurrent logins cannot both observe a count
    below the limit and both insert (the race count_active_sessions() +
    create_session() as two separate calls would allow). Returns the new
    session id, or None if the student is already at max_devices."""
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    expires_at = (now + timedelta(seconds=ttl_seconds)).isoformat()
    session_id = f"sess_{uuid.uuid4().hex}"
    with store.connect() as con:
        # BEGIN IMMEDIATE acquires SQLite's reserved write lock before the
        # count is read, so a concurrent call blocks here (waiting on the
        # lock) rather than reading a stale count and racing to insert. A
        # plain SELECT does not start a transaction under Python's default
        # sqlite3 isolation mode, which is what made the two-call pattern
        # (count_active_sessions() then create_session()) unsafe.
        con.execute("BEGIN IMMEDIATE")
        row = con.execute(
            "SELECT COUNT(*) AS n FROM student_sessions WHERE student_id = ? AND revoked_at IS NULL AND expires_at > ?",
            (student_id, now_iso),
        ).fetchone()
        active_count = int(row["n"]) if row else 0
        if active_count >= max_devices:
            return None
        con.execute(
            """
            INSERT INTO student_sessions
                (id, student_id, refresh_token_hash, user_agent, ip_address, created_at, last_seen_at, expires_at, revoked_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """,
            (session_id, student_id, refresh_token_hash, user_agent, ip_address, now_iso, now_iso, expires_at),
        )
    return session_id


def find_session_by_refresh_hash(store: SecurityStore, refresh_token_hash: str) -> dict | None:
    row = store.fetch_one(
        "SELECT * FROM student_sessions WHERE refresh_token_hash = ? AND revoked_at IS NULL AND expires_at > ?",
        (refresh_token_hash, _utc_now_iso()),
    )
    return dict(row) if row else None


def revoke_session(store: SecurityStore, session_id: str) -> None:
    store.execute(
        "UPDATE student_sessions SET revoked_at = ? WHERE id = ?",
        (_utc_now_iso(), session_id),
    )


def touch_session(store: SecurityStore, session_id: str) -> None:
    store.execute(
        "UPDATE student_sessions SET last_seen_at = ? WHERE id = ?",
        (_utc_now_iso(), session_id),
    )


def list_active_sessions(store: SecurityStore, student_id: str) -> list[dict]:
    now = _utc_now_iso()
    rows = store.fetch_all(
        """
        SELECT id, user_agent, ip_address, created_at, last_seen_at, expires_at
        FROM student_sessions
        WHERE student_id = ? AND revoked_at IS NULL AND expires_at > ?
        ORDER BY last_seen_at DESC
        """,
        (student_id, now),
    )
    return [dict(row) for row in rows]
