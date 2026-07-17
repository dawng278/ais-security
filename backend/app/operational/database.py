from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from app.config import settings
from app.operational.time import utc_now_iso


SCHEMA_VERSION = 1


def parse_sqlite_path(database_url: str) -> Path:
    if database_url == "sqlite:///:memory:":
        return Path(":memory:")
    if not database_url.startswith("sqlite:///"):
        raise ValueError("Phase 4 pilot persistence only supports sqlite:/// URLs")
    return Path(database_url.removeprefix("sqlite:///")).expanduser()


def active_database_url() -> str:
    return settings.test_database_url or settings.security_database_url


def assert_isolated_test_database(database_url: str | None = None) -> None:
    url = database_url or active_database_url()
    if not (url == "sqlite:///:memory:" or "test" in url.lower() or os.environ.get("TEST_DATABASE_URL")):
        raise RuntimeError("Refusing destructive database test without isolated TEST_DATABASE_URL")


SCHEMA_SQL = [
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
      version INTEGER PRIMARY KEY,
      applied_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS integration_clients (
      client_id TEXT PRIMARY KEY,
      display_name TEXT NOT NULL,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS security_decisions (
      decision_id TEXT PRIMARY KEY,
      request_id TEXT NOT NULL UNIQUE,
      correlation_id TEXT NOT NULL,
      client_id TEXT NOT NULL,
      submission_id TEXT NOT NULL,
      pseudonymous_user_id TEXT,
      task_type TEXT NOT NULL,
      language TEXT NOT NULL,
      operating_mode TEXT NOT NULL,
      risk_score REAL NOT NULL,
      severity TEXT NOT NULL,
      techniques_json TEXT NOT NULL,
      detector_health_json TEXT NOT NULL,
      selected_action TEXT NOT NULL,
      counterfactual_action TEXT,
      policy_id TEXT NOT NULL,
      policy_version TEXT NOT NULL,
      grader_status TEXT NOT NULL,
      review_state TEXT NOT NULL,
      final_outcome TEXT NOT NULL,
      latency_ms REAL NOT NULL,
      redaction_state TEXT NOT NULL,
      safe_preview TEXT NOT NULL,
      content_hash TEXT NOT NULL,
      restricted_evidence_json TEXT NOT NULL,
      version INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_security_decisions_correlation ON security_decisions(correlation_id)",
    "CREATE INDEX IF NOT EXISTS idx_security_decisions_client_time ON security_decisions(client_id, created_at)",
    "CREATE INDEX IF NOT EXISTS idx_security_decisions_action_time ON security_decisions(selected_action, created_at)",
    """
    CREATE TABLE IF NOT EXISTS detector_results (
      detector_result_id TEXT PRIMARY KEY,
      decision_id TEXT NOT NULL,
      detector_id TEXT NOT NULL,
      runtime_health TEXT NOT NULL,
      score_contribution REAL NOT NULL,
      confidence REAL NOT NULL,
      techniques_json TEXT NOT NULL,
      safe_evidence_json TEXT NOT NULL,
      latency_ms REAL NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY(decision_id) REFERENCES security_decisions(decision_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS audit_events (
      event_id TEXT PRIMARY KEY,
      correlation_id TEXT NOT NULL,
      actor_subject TEXT NOT NULL,
      actor_type TEXT NOT NULL,
      action TEXT NOT NULL,
      target_type TEXT NOT NULL,
      target_id TEXT NOT NULL,
      environment TEXT NOT NULL,
      policy_version TEXT,
      safe_metadata_json TEXT NOT NULL,
      redaction_state TEXT NOT NULL,
      outcome TEXT NOT NULL,
      reason_code TEXT NOT NULL,
      created_at TEXT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_audit_correlation ON audit_events(correlation_id)",
    "CREATE INDEX IF NOT EXISTS idx_audit_target ON audit_events(target_type, target_id)",
    """
    CREATE TABLE IF NOT EXISTS security_incidents (
      incident_id TEXT PRIMARY KEY,
      decision_id TEXT NOT NULL,
      correlation_id TEXT NOT NULL,
      severity TEXT NOT NULL,
      status TEXT NOT NULL,
      techniques_json TEXT NOT NULL,
      selected_action TEXT NOT NULL,
      assignee TEXT,
      opened_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      resolved_at TEXT,
      resolution TEXT,
      safe_summary TEXT NOT NULL,
      restricted_evidence_ref TEXT NOT NULL,
      version INTEGER NOT NULL DEFAULT 1,
      FOREIGN KEY(decision_id) REFERENCES security_decisions(decision_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS manual_reviews (
      review_id TEXT PRIMARY KEY,
      decision_id TEXT NOT NULL,
      incident_id TEXT,
      correlation_id TEXT NOT NULL,
      state TEXT NOT NULL,
      priority TEXT NOT NULL,
      sla_deadline TEXT NOT NULL,
      assignee TEXT,
      safe_content_preview TEXT NOT NULL,
      resolution TEXT,
      version INTEGER NOT NULL DEFAULT 1,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      FOREIGN KEY(decision_id) REFERENCES security_decisions(decision_id),
      FOREIGN KEY(incident_id) REFERENCES security_incidents(incident_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_manual_reviews_state ON manual_reviews(state, updated_at)",
    """
    CREATE TABLE IF NOT EXISTS review_notes (
      note_id TEXT PRIMARY KEY,
      review_id TEXT NOT NULL,
      actor_subject TEXT NOT NULL,
      note_redacted TEXT NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY(review_id) REFERENCES manual_reviews(review_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS security_policies (
      policy_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      active_version_id TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS security_policy_versions (
      version_id TEXT PRIMARY KEY,
      policy_id TEXT NOT NULL,
      version TEXT NOT NULL,
      status TEXT NOT NULL,
      policy_json TEXT NOT NULL,
      checksum TEXT NOT NULL,
      created_by TEXT NOT NULL,
      approved_by TEXT,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      published_at TEXT,
      UNIQUE(policy_id, version),
      FOREIGN KEY(policy_id) REFERENCES security_policies(policy_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS operating_mode_state (
      singleton_id TEXT PRIMARY KEY CHECK(singleton_id = 'global'),
      mode TEXT NOT NULL,
      previous_mode TEXT,
      active_policy_version_id TEXT,
      reason_code TEXT NOT NULL,
      version INTEGER NOT NULL,
      updated_by TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS idempotency_records (
      scoped_key TEXT PRIMARY KEY,
      actor_scope TEXT NOT NULL,
      request_fingerprint TEXT NOT NULL,
      status TEXT NOT NULL,
      response_json TEXT,
      target_id TEXT,
      expires_at TEXT NOT NULL,
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS evidence_run_references (
      reference_id TEXT PRIMARY KEY,
      run_id TEXT NOT NULL,
      phase TEXT NOT NULL,
      checksum TEXT NOT NULL,
      path TEXT NOT NULL,
      created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS rate_limit_buckets (
      bucket_key TEXT PRIMARY KEY,
      route TEXT NOT NULL,
      actor_scope TEXT NOT NULL,
      window_start INTEGER NOT NULL,
      count INTEGER NOT NULL,
      updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS metrics_events (
      metric_id TEXT PRIMARY KEY,
      name TEXT NOT NULL,
      value REAL NOT NULL,
      labels_json TEXT NOT NULL,
      created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS students (
        id TEXT PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        full_name TEXT,
        phone TEXT,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS student_sessions (
        id TEXT PRIMARY KEY,
        student_id TEXT NOT NULL REFERENCES students(id),
        refresh_token_hash TEXT NOT NULL,
        user_agent TEXT,
        ip_address TEXT,
        created_at TEXT NOT NULL,
        last_seen_at TEXT NOT NULL,
        expires_at TEXT NOT NULL,
        revoked_at TEXT
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_student_sessions_student ON student_sessions(student_id, revoked_at, expires_at)",
]


@dataclass
class SecurityStore:
    database_url: str | None = None

    def __post_init__(self) -> None:
        self.database_url = self.database_url or active_database_url()
        self.path = parse_sqlite_path(self.database_url)
        if self.path != Path(":memory:"):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self.apply_migrations()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        con = sqlite3.connect(str(self.path))
        con.row_factory = sqlite3.Row
        try:
            con.execute("PRAGMA foreign_keys = ON")
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def apply_migrations(self) -> dict[str, Any]:
        with self.connect() as con:
            for statement in SCHEMA_SQL:
                con.execute(statement)
            con.execute(
                "INSERT OR IGNORE INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (SCHEMA_VERSION, utc_now_iso()),
            )
            con.execute(
                """
                INSERT OR IGNORE INTO operating_mode_state(
                  singleton_id, mode, previous_mode, active_policy_version_id, reason_code, version, updated_by, updated_at
                ) VALUES ('global', 'shadow', NULL, NULL, 'GG_REASON_INITIAL_SHADOW', 1, 'system', ?)
                """,
                (utc_now_iso(),),
            )
        return {"schema_version": SCHEMA_VERSION, "database_type": "sqlite", "database_url": self.database_url}

    def fetch_one(self, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self.connect() as con:
            row = con.execute(query, params).fetchone()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def execute(self, query: str, params: tuple[Any, ...] = ()) -> None:
        with self.connect() as con:
            con.execute(query, params)

    def audit(
        self,
        *,
        correlation_id: str,
        actor_subject: str,
        actor_type: str,
        action: str,
        target_type: str,
        target_id: str,
        environment: str,
        policy_version: str | None,
        safe_metadata: dict[str, Any],
        redaction_state: str = "redacted",
        outcome: str = "success",
        reason_code: str = "GG_REASON_RECORDED",
    ) -> str:
        event_id = f"evt_{uuid.uuid4()}"
        self.execute(
            """
            INSERT INTO audit_events(
              event_id, correlation_id, actor_subject, actor_type, action, target_type, target_id,
              environment, policy_version, safe_metadata_json, redaction_state, outcome, reason_code, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                correlation_id,
                actor_subject,
                actor_type,
                action,
                target_type,
                target_id,
                environment,
                policy_version,
                json.dumps(safe_metadata, sort_keys=True),
                redaction_state,
                outcome,
                reason_code,
                utc_now_iso(),
            ),
        )
        return event_id

    def current_mode(self) -> dict[str, Any]:
        row = self.fetch_one("SELECT * FROM operating_mode_state WHERE singleton_id = 'global'")
        assert row is not None
        return row

    def set_mode(
        self,
        *,
        mode: str,
        expected_version: int,
        actor_subject: str,
        reason_code: str,
        active_policy_version_id: str | None = None,
    ) -> dict[str, Any] | None:
        current = self.current_mode()
        if int(current["version"]) != expected_version:
            return None
        with self.connect() as con:
            con.execute(
                """
                UPDATE operating_mode_state
                SET mode = ?, previous_mode = ?, active_policy_version_id = COALESCE(?, active_policy_version_id),
                    reason_code = ?, version = version + 1, updated_by = ?, updated_at = ?
                WHERE singleton_id = 'global' AND version = ?
                """,
                (mode, current["mode"], active_policy_version_id, reason_code, actor_subject, utc_now_iso(), expected_version),
            )
        return self.current_mode()


_STORE: SecurityStore | None = None


def get_store() -> SecurityStore:
    global _STORE
    url = active_database_url()
    if _STORE is None or _STORE.database_url != url:
        _STORE = SecurityStore(url)
    return _STORE


def reset_store_for_tests(database_url: str) -> SecurityStore:
    global _STORE
    _STORE = SecurityStore(database_url)
    return _STORE

