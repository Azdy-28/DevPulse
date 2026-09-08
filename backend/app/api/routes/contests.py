from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.contest import Bookmark
from app.models.user import User
from app.schemas.contest import ContestOut, BookmarkCreate, BookmarkOut
from app.services import aggregator

router = APIRouter(prefix="/api/contests", tags=["contests"])


@router.get("", response_model=list[ContestOut])
async def list_upcoming_contests(
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Aggregated + normalized + cached upcoming contests (requirements #1, #2).
    Marks each contest with whether the current user has bookmarked it.
    """
    contests = await aggregator.get_upcoming_contests(force_refresh=refresh)

    bookmarked_keys = {
        (b.platform, b.external_id)
        for b in db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    }
    for contest in contests:
        contest.is_bookmarked = (contest.platform, contest.external_id) in bookmarked_keys

    return contests


@router.get("/bookmarks", response_model=list[BookmarkOut])
def list_bookmarks(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Bookmark).filter(Bookmark.user_id == current_user.id).order_by(Bookmark.start_time).all()


@router.post("/bookmarks", response_model=BookmarkOut, status_code=201)
def add_bookmark(
    payload: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = (
        db.query(Bookmark)
        .filter(
            Bookmark.user_id == current_user.id,
            Bookmark.platform == payload.platform,
            Bookmark.external_id == payload.external_id,
        )
        .first()
    )
    if existing:
        return existing

    bookmark = Bookmark(user_id=current_user.id, **payload.model_dump())
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


@router.delete("/bookmarks/{bookmark_id}", status_code=204)
def remove_bookmark(
    bookmark_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.query(Bookmark).filter(
        Bookmark.id == bookmark_id, Bookmark.user_id == current_user.id
    ).delete()
    db.commit()
    return None
