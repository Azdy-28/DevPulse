"""
Application settings, loaded from environment variables (.env in dev).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "DevPulse"
    ENVIRONMENT: str = "development"

    # --- Database ---
    # Defaults to the local Postgres instance created for this project.
    # Swap this for any Postgres connection string in production, e.g.
    # postgresql+psycopg2://user:password@host:5432/devpulse
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/devpulse"

    # --- Auth ---
    SECRET_KEY: str = "change-this-secret-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24h

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # --- Frontend (used to redirect back after OAuth login) ---
    FRONTEND_URL: str = "http://localhost:5173"

    # --- OAuth: Google ---
    # Create credentials at https://console.cloud.google.com/apis/credentials
    # Authorized redirect URI must exactly match GOOGLE_REDIRECT_URI below.
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # --- OAuth: Microsoft ---
    # Register an app at https://portal.azure.com under Microsoft Entra ID > App registrations.
    # Add GOOGLE_REDIRECT_URI's Microsoft equivalent as a Web platform redirect URI.
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT: str = "common"  # "common" allows both personal + work/school accounts
    MICROSOFT_REDIRECT_URI: str = "http://localhost:8000/api/auth/microsoft/callback"

    # --- Contest cache ---
    CONTEST_CACHE_TTL_SECONDS: int = 600  # 10 minutes
    CONTEST_FETCH_TIMEOUT_SECONDS: float = 8.0

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
