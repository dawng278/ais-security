from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout_seconds: int = 30
    state: str = "closed"
    failures: int = 0
    opened_at: float | None = None

    def before_call(self) -> str:
        if self.state == "open" and self.opened_at is not None:
            if time() - self.opened_at >= self.recovery_timeout_seconds:
                self.state = "half-open"
        return self.state

    def record_success(self) -> None:
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = time()

