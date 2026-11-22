"""Small helpers: TTL cache, hashing, token/cost estimation, safe logging."""
from __future__ import annotations

import hashlib
import logging
import time
from collections import OrderedDict
from typing import Any, Callable


class TTLCache:
    """Tiny in-memory cache with expiry and a max size (oldest entries evicted)."""

    def __init__(self, ttl_seconds: int = 3600, max_size: int = 128, clock: Callable[[], float] = time.monotonic):
        self.ttl, self.max_size, self._clock = ttl_seconds, max_size, clock
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        stored_at, value = entry
        if self._clock() - stored_at > self.ttl:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (self._clock(), value)
        self._store.move_to_end(key)
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()


def content_hash(*parts: str) -> str:
    return hashlib.sha256("\x1f".join(parts).encode("utf-8")).hexdigest()[:16]


def estimate_tokens(text: str) -> int:
    """Rough estimate (~4 characters per token for English text)."""
    return max(1, len(text) // 4)


def estimate_cost_usd(input_tokens: int, output_tokens: int, price_in_per_1m: float, price_out_per_1m: float) -> float:
    return (input_tokens * price_in_per_1m + output_tokens * price_out_per_1m) / 1_000_000


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("opener_app")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
