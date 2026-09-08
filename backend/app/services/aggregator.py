"""
Fetches upcoming contests from every platform CONCURRENTLY (requirement #1)
and merges them into one sorted, normalized list, backed by a TTL cache
(requirement #2) so repeated dashboard loads are fast and don't hammer
external services.
"""
import asyncio
import logging
import time

import httpx

from app.core.config import get_settings
from app.schemas.contest import ContestOut
from app.services.cache import TTLCache
from app.services.contest_providers.codeforces import CodeforcesProvider
from app.services.contest_providers.leetcode import LeetCodeProvider
from app.services.contest_providers.codechef import CodeChefProvider

logger = logging.getLogger(__name__)
settings = get_settings()

PROVIDERS = [CodeforcesProvider(), LeetCodeProvider(), CodeChefProvider()]

_cache = TTLCache(ttl_seconds=settings.CONTEST_CACHE_TTL_SECONDS)


async def _fetch_all_platforms() -> list[ContestOut]:
    async with httpx.AsyncClient(timeout=settings.CONTEST_FETCH_TIMEOUT_SECONDS) as client:
        results = await asyncio.gather(
            *(provider.fetch_upcoming(client) for provider in PROVIDERS),
            return_exceptions=True,
        )

    all_contests: list[ContestOut] = []
    for provider, result in zip(PROVIDERS, results):
        if isinstance(result, Exception):
            logger.warning("Provider %s raised unexpectedly: %s", provider.platform, result)
            continue
        all_contests.extend(result)

    all_contests.sort(key=lambda c: c.start_time)
    return all_contests


async def get_upcoming_contests(force_refresh: bool = False) -> list[ContestOut]:
    if force_refresh:
        contests = await _fetch_all_platforms()
        _cache._value = contests
        _cache._fetched_at = time.monotonic()
        return contests
    return await _cache.get_or_refresh(_fetch_all_platforms)


def cache_age_seconds() -> float | None:
    return _cache.age_seconds()
