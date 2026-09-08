import datetime as dt
from pydantic import BaseModel
from app.models.activity import ActivityType


class ActivityCreate(BaseModel):
    type: ActivityType
    title: str
    description: str | None = None
    goal_id: int | None = None
    extra_data: dict | None = None
    occurred_at: dt.datetime | None = None


class ActivityOut(BaseModel):
    id: int
    type: ActivityType
    title: str
    description: str | None
    goal_id: int | None
    extra_data: dict | None
    occurred_at: dt.datetime

    class Config:
        from_attributes = True
