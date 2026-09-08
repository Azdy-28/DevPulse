"""
Per-user platform stats: pulls rating/rank/solved-count for whichever
handles a user has linked on their profile. This is what actually makes
saving a handle *do* something, as opposed to just storing a string.

Each fetch function fails closed (returns an error string instead of
raising) so one bad/misspelled handle or one platform's endpoint changing
doesn't break the others.
"""
import asyncio
import logging
import re

import httpx

from app.core.config import get_settings
from app.services.cache import KeyedTTLCache

logger = logging.getLogger(__name__)
settings = get_settings()

# Keyed by (user_id, platform) so each platform's cache invalidates independently.
_stats_cache = KeyedTTLCache(ttl_seconds=settings.CONTEST_CACHE_TTL_SECONDS)


async def _fetch_codeforces(client: httpx.AsyncClient, handle: str) -> dict:
    try:
        resp = await client.get("https://codeforces.com/api/user.info", params={"handles": handle})
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "OK":
            return {"handle": handle, "error": "Handle not found"}
        info = data["result"][0]
        return {
            "handle": handle,
            "rating": info.get("rating"),
            "max_rating": info.get("maxRating"),
            "rank": info.get("rank"),
            "solved": None,  # Codeforces API doesn't expose a solved count directly
        }
    except (httpx.HTTPError, KeyError, IndexError, ValueError) as exc:
        logger.warning("Codeforces stats fetch failed for %s: %s", handle, exc)
        return {"handle": handle, "error": "Could not reach Codeforces"}


LEETCODE_STATS_QUERY = """
query userStats($username: String!) {
  matchedUser(username: $username) {
    username
    profile { ranking }
    submitStatsGlobal {
      acSubmissionNum { difficulty count }
    }
  }
}
"""


async def _fetch_leetcode(client: httpx.AsyncClient, handle: str) -> dict:
    try:
        resp = await client.post(
            "https://leetcode.com/graphql",
            json={"query": LEETCODE_STATS_QUERY, "variables": {"username": handle}},
            headers={"Content-Type": "application/json", "Referer": f"https://leetcode.com/{handle}/"},
        )
        resp.raise_for_status()
        data = resp.json()
        user = (data.get("data") or {}).get("matchedUser")
        if not user:
            return {"handle": handle, "error": "Handle not found"}

        solved_total = 0
        for entry in user.get("submitStatsGlobal", {}).get("acSubmissionNum", []):
            if entry.get("difficulty") == "All":
                solved_total = entry.get("count", 0)

        return {
            "handle": handle,
            "rating": None,
            "rank": user.get("profile", {}).get("ranking"),
            "solved": solved_total,
        }
    except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
        logger.warning("LeetCode stats fetch failed for %s: %s", handle, exc)
        return {"handle": handle, "error": "Could not reach LeetCode"}


# CodeChef has no API for public profiles, official or otherwise. Their
# profile page embeds a small JS object with the rating in it - this
# regex pulls it out. Genuinely fragile: if CodeChef changes their page
# markup this will start returning "Could not read CodeChef profile"
# until the pattern below is updated to match.
CODECHEF_RATING_RE = re.compile(r'"rating"\s*:\s*"?(\d+)"?')
CODECHEF_STARS_RE = re.compile(r'class="rating"[^>]*>([^<]+)<')


async def _fetch_codechef(client: httpx.AsyncClient, handle: str) -> dict:
    try:
        resp = await client.get(f"https://www.codechef.com/users/{handle}")
        if resp.status_code == 404:
            return {"handle": handle, "error": "Handle not found"}
        resp.raise_for_status()
        html = resp.text

        rating_match = CODECHEF_RATING_RE.search(html)
        rating = int(rating_match.group(1)) if rating_match else None

        return {
            "handle": handle,
            "rating": rating,
            "rank": None,
            "solved": None,
        }
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("CodeChef stats fetch failed for %s: %s", handle, exc)
        return {"handle": handle, "error": "Could not read CodeChef profile"}


_FETCHERS = {
    "codeforces": _fetch_codeforces,
    "leetcode": _fetch_leetcode,
    "codechef": _fetch_codechef,
}


async def get_user_platform_stats(user_id: int, handles: dict[str, str | None], force_refresh: bool = False) -> dict:
    """
    handles: {"codeforces": "tourist", "leetcode": None, "codechef": "someone"}
    Returns: {"codeforces": {...}, "leetcode": None, "codechef": {...}}
    Platforms with no handle set are returned as None (not fetched at all).
    Platforms that do have a handle are fetched concurrently.
    """
    async with httpx.AsyncClient(timeout=settings.CONTEST_FETCH_TIMEOUT_SECONDS, follow_redirects=True) as client:
        active = {platform: handle for platform, handle in handles.items() if handle}

        async def fetch_one(platform: str, handle: str):
            cache_key = (user_id, platform, handle)
            fetcher = _FETCHERS[platform]
            if force_refresh:
                _stats_cache.invalidate(cache_key)
            return platform, await _stats_cache.get_or_refresh(cache_key, lambda: fetcher(client, handle))

        fetched = await asyncio.gather(*(fetch_one(p, h) for p, h in active.items()))

        results: dict = {platform: None for platform in handles}
        for platform, stats in fetched:
            results[platform] = stats
        return results
