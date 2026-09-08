from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserOut, UserProfileUpdate, PlatformStatsOut
from app.services import platform_stats

router = APIRouter(prefix="/api/profile", tags=["profile"])


def _handles_dict(user: User) -> dict:
    return {
        "codeforces": user.codeforces_handle,
        "leetcode": user.leetcode_handle,
        "codechef": user.codechef_handle,
    }


@router.put("", response_model=UserOut)
def update_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/stats", response_model=PlatformStatsOut)
async def get_platform_stats(
    refresh: bool = False,
    current_user: User = Depends(get_current_user),
):
    """
    Pulls live rating/rank/solved-count for every platform handle the user
    has linked, fetched concurrently and cached per-user for a few minutes.
    `refresh=true` forces a bypass of that cache (used by the "Sync now"
    button and right after saving new handles).
    """
    stats = await platform_stats.get_user_platform_stats(
        user_id=current_user.id,
        handles=_handles_dict(current_user),
        force_refresh=refresh,
    )
    return PlatformStatsOut(**stats)
