import datetime as dt
from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    codeforces_handle: str | None = None
    leetcode_handle: str | None = None
    codechef_handle: str | None = None
    github_username: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str | None
    codeforces_handle: str | None
    leetcode_handle: str | None
    codechef_handle: str | None
    github_username: str | None
    created_at: dt.datetime


class PlatformStat(BaseModel):
    handle: str
    rating: int | None = None
    max_rating: int | None = None
    rank: str | int | None = None
    solved: int | None = None
    error: str | None = None


class PlatformStatsOut(BaseModel):
    codeforces: PlatformStat | None = None
    leetcode: PlatformStat | None = None
    codechef: PlatformStat | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
