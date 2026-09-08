import datetime as dt
from pydantic import BaseModel


class ContestOut(BaseModel):
    """Normalized contest shape, common across all platforms."""
    platform: str            # "codeforces" | "leetcode" | "codechef"
    external_id: str
    name: str
    start_time: dt.datetime
    duration_minutes: int
    url: str
    is_bookmarked: bool = False


class BookmarkCreate(BaseModel):
    platform: str
    external_id: str
    name: str
    start_time: dt.datetime
    url: str


class BookmarkOut(BookmarkCreate):
    id: int

    class Config:
        from_attributes = True
