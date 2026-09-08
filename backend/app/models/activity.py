import datetime as dt
import enum

from sqlalchemy import String, DateTime, ForeignKey, Text, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ActivityType(str, enum.Enum):
    contest = "contest"          # participated in a contest
    learning = "learning"        # completed a course/topic/roadmap item
    project = "project"          # project milestone
    github = "github"            # github activity (future: auto-synced)
    other = "other"


class ActivityLog(Base):
    """
    A record of something the developer did. This is the raw timeline
    that dashboard stats and (eventually) insights are derived from.
    """
    __tablename__ = "activity_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    goal_id: Mapped[int | None] = mapped_column(ForeignKey("goals.id"), nullable=True)

    type: Mapped[ActivityType] = mapped_column(Enum(ActivityType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # flexible per-type metadata
    occurred_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    user = relationship("User", back_populates="activities")
    goal = relationship("Goal", back_populates="activities")
