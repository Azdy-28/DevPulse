"""
CodeChef adapter.

CodeChef also has no official public contest-list API. This uses the
unofficial endpoint that codechef.com's own site consumes. Same
fail-closed policy as the LeetCode provider.
"""
import datetime as dt
import logging

import httpx

from app.schemas.contest import ContestOut
from app.services.contest_providers.base import ContestProvider

logger = logging.getLogger(__name__)

CODECHEF_API = "https://www.codechef.com/api/list/contests/all"


class CodeChefProvider(ContestProvider):
    platform = "codechef"

    async def fetch_upcoming(self, client: httpx.AsyncClient) -> list[ContestOut]:
        try:
            resp = await client.get(CODECHEF_API, params={"sort_by": "START", "sorting_order": "asc"})
            resp.raise_for_status()
            data = resp.json()

            contests: list[ContestOut] = []
            for item in data.get("future_contests", []):
                start_str = item.get("contest_start_date_iso")
                if not start_str:
                    continue
                start_time = dt.datetime.fromisoformat(start_str.replace("Z", "+00:00"))
                end_str = item.get("contest_end_date_iso")
                duration_minutes = 0
                if end_str:
                    end_time = dt.datetime.fromisoformat(end_str.replace("Z", "+00:00"))
                    duration_minutes = int((end_time - start_time).total_seconds() // 60)

                contests.append(
                    ContestOut(
                        platform=self.platform,
                        external_id=item["contest_code"],
                        name=item["contest_name"],
                        start_time=start_time,
                        duration_minutes=duration_minutes,
                        url=f"https://www.codechef.com/{item['contest_code']}",
                    )
                )
            return contests
        except (httpx.HTTPError, KeyError, ValueError) as exc:
            logger.warning("CodeChef fetch failed (unofficial endpoint may have changed): %s", exc)
            return []
