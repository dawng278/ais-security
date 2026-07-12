from __future__ import annotations

from dataclasses import dataclass

from app.operational.database import SecurityStore


@dataclass(frozen=True)
class RetentionDryRun:
    mode: str
    categories: dict[str, int]
    execution_supported: bool
    destructive_action_taken: bool = False


def retention_dry_run(store: SecurityStore) -> RetentionDryRun:
    categories = {
        "idempotency_records": store.fetch_one("SELECT COUNT(*) AS count FROM idempotency_records")["count"],
        "decision_metadata": store.fetch_one("SELECT COUNT(*) AS count FROM security_decisions")["count"],
        "incidents": store.fetch_one("SELECT COUNT(*) AS count FROM security_incidents")["count"],
        "manual_reviews": store.fetch_one("SELECT COUNT(*) AS count FROM manual_reviews")["count"],
        "audit_events": store.fetch_one("SELECT COUNT(*) AS count FROM audit_events")["count"],
    }
    return RetentionDryRun(mode="dry_run_only", categories=categories, execution_supported=False)

