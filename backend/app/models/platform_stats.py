import datetime as dt

from sqlalchemy import String, DateTime, ForeignKey, Integer, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class PlatformStats(Base):
    """
    Synced snapshot of a user's stats on one external platform (rating,
    rank, solved count, etc). Populated by services/profile_providers/*
    whenever a handle is saved or a manual sync is requested - kept in
    Postgres (not re-fetched on every page load) for the same reason
    contests are cached: don't hammer external services on every request.
    """
    __tablename__ = "platform_stats"
    __table_args__ = (UniqueConstraint("user_id", "platform", name="uq_user_platform"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    platform: Mapped[str] = mapped_column(String(50), nullable=False)   # "codeforces" | "leetcode" | "codechef"
    handle: Mapped[str] = mapped_column(String(100), nullable=False)

    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rank: Mapped[str | None] = mapped_column(String(100), nullable=True)
    solved_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    synced_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)
    sync_error: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user = relationship("User")
