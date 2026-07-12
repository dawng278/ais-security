from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from app.operational.database import SecurityStore
from app.operational.redaction import redact_text
from app.operational.time import utc_now_iso


LOGGER = logging.getLogger("gradingguard.operational")


def safe_log(level: int, message: str, **metadata: Any) -> None:
    safe_metadata = {}
    for key, value in metadata.items():
        if value is None:
            continue
        text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, default=str)
        safe_metadata[key] = redact_text(text, max_preview=180).preview
    LOGGER.log(level, "%s %s", message, json.dumps(safe_metadata, sort_keys=True))


def record_metric(store: SecurityStore, name: str, value: float, labels: dict[str, Any]) -> None:
    safe_labels = {
        key: str(value)
        for key, value in labels.items()
        if key in {"route", "action", "severity", "mode", "detector", "status", "error_code"}
    }
    store.execute(
        "INSERT INTO metrics_events(metric_id, name, value, labels_json, created_at) VALUES (?, ?, ?, ?, ?)",
        (f"met_{uuid.uuid4()}", name, value, json.dumps(safe_labels, sort_keys=True), utc_now_iso()),
    )


def metric_summary(store: SecurityStore) -> dict[str, Any]:
    rows = store.fetch_all("SELECT name, COUNT(*) AS count FROM metrics_events GROUP BY name ORDER BY name")
    return {"status": "available", "high_cardinality_guard": "enabled", "metrics": rows}

