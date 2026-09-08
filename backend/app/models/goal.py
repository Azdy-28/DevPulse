import datetime as dt
import enum

from sqlalchemy import String, DateTime, ForeignKey, Integer, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class GoalStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class Goal(Base):
    """
    A target the developer is working toward, e.g. 'Improve DSA',
    'Finish backend roadmap', 'Prep for SDE interviews'.
    """
    __tablename__ = "goals"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, default="general")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[GoalStatus] = mapped_column(Enum(GoalStatus), default=GoalStatus.not_started)
    progress: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    target_date: Mapped[dt.date | None] = mapped_column(nullable=True)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow
    )

    user = relationship("User", back_populates="goals")
    activities = relationship("ActivityLog", back_populates="goal")
