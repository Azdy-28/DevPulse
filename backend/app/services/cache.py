"""
Small async, in-process TTL cache.

Purpose (requirement #2): keep a fast cached snapshot of aggregated contest
data so the frontend never triggers a live fan-out to Codeforces/LeetCode/
CodeChef on every dashboard load. A single asyncio.Lock prevents a
"thundering herd" of concurrent requests all refetching at once when the
cache expires - only the first caller refreshes, the rest wait on the lock
and then read the fresh value.

This is intentionally dependency-free (no Redis) so the project runs
anywhere; swapping in Redis later just means replacing this class's
internals behind the same get/set interface.
"""
import asyncio
import time
from typing import Any, Awaitable, Callable


class TTLCache:
    def __init__(self, ttl_seconds: int):
        self._ttl = ttl_seconds
        self._value: Any = None
        self._fetched_at: float = 0.0
        self._lock = asyncio.Lock()

    def _is_stale(self) -> bool:
        return self._value is None or (time.monotonic() - self._fetched_at) > self._ttl

    async def get_or_refresh(self, refresh_fn: Callable[[], Awaitable[Any]]) -> Any:
        if not self._is_stale():
            return self._value

        async with self._lock:
            # Re-check: another request may have refreshed while we waited for the lock.
            if not self._is_stale():
                return self._value
            self._value = await refresh_fn()
            self._fetched_at = time.monotonic()
            return self._value

    def age_seconds(self) -> float | None:
        if self._value is None:
            return None
        return time.monotonic() - self._fetched_at


class KeyedTTLCache:
    """
    Same idea as TTLCache, but keyed - used for per-user platform stats where
    each user's cached snapshot needs its own TTL bucket instead of one
    global value.
    """
    def __init__(self, ttl_seconds: int):
        self._ttl = ttl_seconds
        self._store: dict[Any, tuple[Any, float]] = {}
        self._locks: dict[Any, asyncio.Lock] = {}

    def _lock_for(self, key: Any) -> asyncio.Lock:
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    def _is_stale(self, key: Any) -> bool:
        entry = self._store.get(key)
        if entry is None:
            return True
        _, fetched_at = entry
        return (time.monotonic() - fetched_at) > self._ttl

    async def get_or_refresh(self, key: Any, refresh_fn: Callable[[], Awaitable[Any]]) -> Any:
        if not self._is_stale(key):
            return self._store[key][0]

        async with self._lock_for(key):
            if not self._is_stale(key):
                return self._store[key][0]
            value = await refresh_fn()
            self._store[key] = (value, time.monotonic())
            return value

    def invalidate(self, key: Any) -> None:
        self._store.pop(key, None)

    def age_seconds(self, key: Any) -> float | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        return time.monotonic() - entry[1]
