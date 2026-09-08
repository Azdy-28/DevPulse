import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
from app.api.routes import auth, profile, contests, goals, projects, activity, dashboard

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(contests.router)
app.include_router(goals.router)
app.include_router(projects.router)
app.include_router(activity.router)
app.include_router(dashboard.router)


@app.on_event("startup")
def on_startup():
    # Dev-friendly: create tables if they don't exist. For real schema
    # evolution, replace this with Alembic migrations.
    Base.metadata.create_all(bind=engine)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
