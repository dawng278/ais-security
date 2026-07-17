from __future__ import annotations

import time
from dataclasses import dataclass

from app.config import settings
from app.operational.database import SecurityStore
from app.operational.errors import GatewayException
from app.operational.time import utc_now_iso


@dataclass(frozen=True)
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after_seconds: int


def check_rate_limit(
    store: SecurityStore,
    *,
    actor_scope: str,
    route: str,
    limit: int | None = None,
    window_seconds: int | None = None,
) -> RateLimitResult:
    limit = limit or settings.rate_limit_max_requests
    window_seconds = window_seconds or settings.rate_limit_window_seconds
    now = int(time.time())
    window_start = now - (now % window_seconds)
    bucket_key = f"{route}:{actor_scope}:{window_start}"
    with store.connect() as con:
        # BEGIN IMMEDIATE acquires the write lock before the read, so two
        # concurrent callers for the same bucket_key serialize instead of
        # both observing "no row yet" and racing on the INSERT (which would
        # otherwise raise sqlite3.IntegrityError on the bucket_key UNIQUE
        # constraint under real concurrent load, e.g. many simultaneous
        # login attempts from the same IP).
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT count FROM rate_limit_buckets WHERE bucket_key = ?", (bucket_key,)).fetchone()
        if row is None:
            con.execute(
                """
                INSERT INTO rate_limit_buckets(bucket_key, route, actor_scope, window_start, count, updated_at)
                VALUES (?, ?, ?, ?, 1, ?)
                """,
                (bucket_key, route, actor_scope, window_start, utc_now_iso()),
            )
            return RateLimitResult(True, limit, limit - 1, 0)
        count = int(row["count"]) + 1
        if count > limit:
            retry = window_seconds - (now - window_start)
            raise GatewayException("RATE_LIMITED", detail=f"retry_after:{retry}")
        con.execute(
            "UPDATE rate_limit_buckets SET count = ?, updated_at = ? WHERE bucket_key = ?",
            (count, utc_now_iso(), bucket_key),
        )
        return RateLimitResult(True, limit, max(0, limit - count), 0)

