import datetime as dt

from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Bookmark(Base):
    """
    A user's saved contest. We store a denormalized snapshot (name/start_time/url)
    at bookmark-time rather than a live foreign key into an external system,
    since contest data itself lives in the in-memory cache, not the DB.
    """
    __tablename__ = "bookmarks"
    __table_args__ = (UniqueConstraint("user_id", "platform", "external_id", name="uq_user_contest"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    platform: Mapped[str] = mapped_column(String(50), nullable=False)       # e.g. "codeforces"
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)   # platform-specific contest id
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_time: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)

    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=dt.datetime.utcnow)

    user = relationship("User", back_populates="bookmarks")
