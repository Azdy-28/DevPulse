import datetime as dt
from pydantic import BaseModel
from app.models.goal import GoalStatus


class GoalCreate(BaseModel):
    title: str
    category: str = "general"
    description: str | None = None
    target_date: dt.date | None = None


class GoalUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    description: str | None = None
    status: GoalStatus | None = None
    progress: int | None = None
    target_date: dt.date | None = None


class GoalOut(BaseModel):
    id: int
    title: str
    category: str
    description: str | None
    status: GoalStatus
    progress: int
    target_date: dt.date | None
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True
