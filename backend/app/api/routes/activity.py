from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.activity import ActivityLog
from app.models.user import User
from app.schemas.activity import ActivityCreate, ActivityOut

router = APIRouter(prefix="/api/activity", tags=["activity"])


@router.get("", response_model=list[ActivityOut])
def list_activity(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == current_user.id)
        .order_by(ActivityLog.occurred_at.desc())
        .limit(limit)
        .all()
    )


@router.post("", response_model=ActivityOut, status_code=201)
def log_activity(
    payload: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    import datetime as dt

    data = payload.model_dump()
    if data.get("occurred_at") is None:
        data["occurred_at"] = dt.datetime.utcnow()

    activity = ActivityLog(user_id=current_user.id, **data)
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity


@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db.query(ActivityLog).filter(
        ActivityLog.id == activity_id, ActivityLog.user_id == current_user.id
    ).delete()
    db.commit()
    return None
