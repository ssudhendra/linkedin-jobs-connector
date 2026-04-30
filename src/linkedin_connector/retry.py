from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar


T = TypeVar("T")


def run_with_retry(fn: Callable[[], T], retries: int, delay_seconds: float = 0.25) -> T:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            return fn()
        except Exception as exc:  # pragma: no cover - defensive path
            last_error = exc
            if attempt == retries:
                break
            time.sleep(delay_seconds * (attempt + 1))
    assert last_error is not None
    raise last_error
