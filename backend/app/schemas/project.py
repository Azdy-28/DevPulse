import datetime as dt
from pydantic import BaseModel
from app.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None
    tech_stack: str | None = None
    status: ProjectStatus = ProjectStatus.planning
    repo_url: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    tech_stack: str | None = None
    status: ProjectStatus | None = None
    repo_url: str | None = None


class ProjectOut(BaseModel):
    id: int
    name: str
    description: str | None
    tech_stack: str | None
    status: ProjectStatus
    repo_url: str | None
    created_at: dt.datetime
    updated_at: dt.datetime

    class Config:
        from_attributes = True
