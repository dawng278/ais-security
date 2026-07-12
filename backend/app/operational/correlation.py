from __future__ import annotations

import re
import uuid


CORRELATION_ID_RE = re.compile(r"^[A-Za-z0-9_.:-]{8,96}$")


def resolve_correlation_id(value: str | None) -> str:
    if value is None or value == "":
        return f"corr-{uuid.uuid4()}"
    if not CORRELATION_ID_RE.fullmatch(value):
        return f"corr-{uuid.uuid4()}"
    return value

