from pydantic import BaseModel

from app.schemas.contest import ContestOut
from app.schemas.goal import GoalOut
from app.schemas.project import ProjectOut
from app.schemas.activity import ActivityOut
from app.schemas.user import UserOut


class DashboardStats(BaseModel):
    total_goals: int
    goals_in_progress: int
    goals_completed: int
    total_projects: int
    active_projects: int
    bookmarked_contests: int
    activities_last_30_days: int


class DashboardOut(BaseModel):
    """
    Single aggregated payload for the unified dashboard view (requirement #5):
    one response the frontend renders instead of stitching together
    multiple platform-specific calls.
    """
    user: UserOut
    upcoming_contests: list[ContestOut]
    goals: list[GoalOut]
    projects: list[ProjectOut]
    recent_activity: list[ActivityOut]
    stats: DashboardStats
