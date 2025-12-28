from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field

from app.models import TaskStatus


# ============ Auth Schemas ============

class UserRegister(BaseModel):
    """User registration request."""
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Refresh token request."""
    refresh_token: str


# ============ Project Schemas ============

class ProjectCreate(BaseModel):
    """Create project request."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    """Update project request."""
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Project response."""
    id: int
    name: str
    description: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ Task Schemas ============

class TaskCreate(BaseModel):
    """Create task request."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    due_at: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    priority: int = Field(3, ge=1, le=5)
    tags: List[str] = Field(default_factory=list)
    project_id: int


class TaskUpdate(BaseModel):
    """Update task request."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_at: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None


class TaskResponse(BaseModel):
    """Task response."""
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    due_at: Optional[datetime]
    estimated_minutes: Optional[int]
    priority: int
    ai_score: Optional[float]
    tags: List[str]
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ AI Schemas ============

class TaskForPrioritization(BaseModel):
    """Task input for AI prioritization."""
    title: str
    description: Optional[str] = None
    due_at: Optional[datetime] = None
    estimated_minutes: Optional[int] = None
    importance: int = Field(3, ge=1, le=5)  # 1-5 scale


class PrioritizationRequest(BaseModel):
    """Request to prioritize tasks."""
    tasks: List[TaskForPrioritization] = Field(..., min_items=1, max_items=50)


class PrioritizationResult(BaseModel):
    """Prioritization result for a single task."""
    title: str
    score: float = Field(..., ge=0, le=1)
    rationale: str


class PrioritizationResponse(BaseModel):
    """Full prioritization response."""
    results: List[PrioritizationResult]
    plan: List[str]


# ============ Health & Observability ============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
