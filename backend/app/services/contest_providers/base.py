"""
Common interface every contest-platform adapter implements.

Each provider is responsible ONLY for talking to its own platform and
returning contests in the normalized ContestOut shape. Nothing here knows
about caching, HTTP status codes at the API-route level, or the DB — that
separation is what lets aggregator.py fetch all platforms concurrently and
tolerate any single one failing.
"""
from abc import ABC, abstractmethod

import httpx

from app.schemas.contest import ContestOut


class ContestProvider(ABC):
    platform: str

    @abstractmethod
    async def fetch_upcoming(self, client: httpx.AsyncClient) -> list[ContestOut]:
        """Return normalized upcoming contests. Must not raise — catch and
        log internally, returning [] on failure so one bad platform never
        takes down the whole aggregation."""
        raise NotImplementedError
