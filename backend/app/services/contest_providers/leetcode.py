"""
LeetCode adapter.

LeetCode has no official public REST API for contests. This uses the
community-documented GraphQL endpoint that leetcode.com's own frontend
calls. It is unofficial and may change without notice - if the query
shape ever breaks, this provider fails closed (returns []) rather than
raising, so the rest of the dashboard keeps working.
"""
import datetime as dt
import logging

import httpx

from app.schemas.contest import ContestOut
from app.services.contest_providers.base import ContestProvider

logger = logging.getLogger(__name__)

LEETCODE_GRAPHQL = "https://leetcode.com/graphql"

QUERY = """
query upcomingContests {
  upcomingContests {
    title
    titleSlug
    startTime
    duration
  }
}
"""


class LeetCodeProvider(ContestProvider):
    platform = "leetcode"

    async def fetch_upcoming(self, client: httpx.AsyncClient) -> list[ContestOut]:
        try:
            resp = await client.post(
                LEETCODE_GRAPHQL,
                json={"query": QUERY, "operationName": "upcomingContests"},
                headers={"Content-Type": "application/json", "Referer": "https://leetcode.com/contest/"},
            )
            resp.raise_for_status()
            data = resp.json()
            items = (data.get("data") or {}).get("upcomingContests") or []

            contests: list[ContestOut] = []
            for item in items:
                start_ts = item.get("startTime")
                if start_ts is None:
                    continue
                contests.append(
                    ContestOut(
                        platform=self.platform,
                        external_id=item["titleSlug"],
                        name=item["title"],
                        start_time=dt.datetime.fromtimestamp(start_ts, tz=dt.timezone.utc),
                        duration_minutes=int(item.get("duration", 0) // 60),
                        url=f"https://leetcode.com/contest/{item['titleSlug']}",
                    )
                )
            return contests
        except (httpx.HTTPError, KeyError, ValueError, TypeError) as exc:
            logger.warning("LeetCode fetch failed (unofficial endpoint may have changed): %s", exc)
            return []
