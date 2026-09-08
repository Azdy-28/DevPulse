import datetime as dt

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.activity import ActivityLog
from app.models.contest import Bookmark
from app.models.goal import Goal, GoalStatus
from app.models.project import Project, ProjectStatus
from app.models.user import User
from app.schemas.dashboard import DashboardOut, DashboardStats
from app.services import aggregator

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
async def get_dashboard(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Requirement #5: one call that assembles everything the unified
    dashboard needs, so the React app doesn't have to make five separate
    round trips and stitch the result together itself.
    """
    contests = await aggregator.get_upcoming_contests()
    bookmarked_keys = {
        (b.platform, b.external_id)
        for b in db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    }
    for contest in contests:
        contest.is_bookmarked = (contest.platform, contest.external_id) in bookmarked_keys

    goals = db.query(Goal).filter(Goal.user_id == current_user.id).order_by(Goal.created_at.desc()).all()
    projects = (
        db.query(Project).filter(Project.user_id == current_user.id).order_by(Project.updated_at.desc()).all()
    )
    recent_activity = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.occurred_at.desc())
        .limit(10)
        .all()
    )
    bookmark_count = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).count()

    thirty_days_ago = dt.datetime.utcnow() - dt.timedelta(days=30)
    activities_last_30_days = (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id, ActivityLog.occurred_at >= thirty_days_ago)
        .count()
    )

    stats = DashboardStats(
        total_goals=len(goals),
        goals_in_progress=sum(1 for g in goals if g.status == GoalStatus.in_progress),
        goals_completed=sum(1 for g in goals if g.status == GoalStatus.completed),
        total_projects=len(projects),
        active_projects=sum(1 for p in projects if p.status == ProjectStatus.active),
        bookmarked_contests=bookmark_count,
        activities_last_30_days=activities_last_30_days,
    )

    return DashboardOut(
        user=current_user,
        upcoming_contests=contests[:20],
        goals=goals,
        projects=projects,
        recent_activity=recent_activity,
        stats=stats,
    )
