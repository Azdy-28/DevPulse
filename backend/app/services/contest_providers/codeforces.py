"""
Codeforces adapter.

Uses the official public API: https://codeforces.com/api/contest.list
Docs: https://codeforces.com/apiHelp/methods#contest.list
"""
import datetime as dt
import logging

import httpx

from app.schemas.contest import ContestOut
from app.services.contest_providers.base import ContestProvider

logger = logging.getLogger(__name__)

CODEFORCES_API = "https://codeforces.com/api/contest.list"


class CodeforcesProvider(ContestProvider):
    platform = "codeforces"

    async def fetch_upcoming(self, client: httpx.AsyncClient) -> list[ContestOut]:
        try:
            resp = await client.get(CODEFORCES_API)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != "OK":
                logger.warning("Codeforces API returned non-OK status: %s", data.get("status"))
                return []

            contests: list[ContestOut] = []
            for item in data.get("result", []):
                if item.get("phase") != "BEFORE":
                    continue  # only upcoming contests
                start_ts = item.get("startTimeSeconds")
                if start_ts is None:
                    continue
                contests.append(
                    ContestOut(
                        platform=self.platform,
                        external_id=str(item["id"]),
                        name=item["name"],
                        start_time=dt.datetime.fromtimestamp(start_ts, tz=dt.timezone.utc),
                        duration_minutes=int(item.get("durationSeconds", 0) // 60),
                        url=f"https://codeforces.com/contest/{item['id']}",
                    )
                )
            return contests
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("Codeforces fetch failed: %s", exc)
            return []
