import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core import oauth
from app.core.config import get_settings
from app.core.security import hash_password, verify_password, create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, Token
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses "username" as the field name; we treat it as email.
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not user.hashed_password:
        raise HTTPException(
            status_code=401,
            detail="This account signs in with Google/Microsoft, not a password."
            if user else "Incorrect email or password",
        )
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token(subject=user.email)
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


def _find_or_create_oauth_user(db: Session, email: str, name: str | None, provider: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user
    user = User(email=email, full_name=name, hashed_password=None, oauth_provider=provider)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/google/login")
def google_login():
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google login is not configured on this server.")
    state = secrets.token_urlsafe(16)
    return RedirectResponse(oauth.google_authorize_url(state))


@router.get("/google/callback")
async def google_callback(code: str, db: Session = Depends(get_db)):
    try:
        info = await oauth.google_fetch_user(code)
    except oauth.OAuthError as exc:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error={exc}")

    user = _find_or_create_oauth_user(db, info["email"], info.get("name"), "google")
    token = create_access_token(subject=user.email)
    return RedirectResponse(f"{settings.FRONTEND_URL}/oauth-callback?token={token}")


@router.get("/microsoft/login")
def microsoft_login():
    if not settings.MICROSOFT_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Microsoft login is not configured on this server.")
    state = secrets.token_urlsafe(16)
    return RedirectResponse(oauth.microsoft_authorize_url(state))


@router.get("/microsoft/callback")
async def microsoft_callback(code: str, db: Session = Depends(get_db)):
    try:
        info = await oauth.microsoft_fetch_user(code)
    except oauth.OAuthError as exc:
        return RedirectResponse(f"{settings.FRONTEND_URL}/login?error={exc}")

    user = _find_or_create_oauth_user(db, info["email"], info.get("name"), "microsoft")
    token = create_access_token(subject=user.email)
    return RedirectResponse(f"{settings.FRONTEND_URL}/oauth-callback?token={token}")
