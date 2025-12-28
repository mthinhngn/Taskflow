from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class User(Base):
    """User model for authentication."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    """Project model."""
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class TaskStatus(str, enum.Enum):
    """Task status enum."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    BLOCKED = "blocked"


class Task(Base):
    """Task model."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    due_at = Column(DateTime, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    priority = Column(Integer, default=3)  # 1-5, 1 = lowest
    tags = Column(JSONB, default=list)  # ["tag1", "tag2", ...]
    ai_score = Column(Float, nullable=True)  # AI prioritization score
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    owner = relationship("User", back_populates="tasks")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete-orphan")


class TaskEventType(str, enum.Enum):
    """Task event types."""
    CREATED = "created"
    UPDATED = "updated"
    STATUS_CHANGED = "status_changed"
    PRIORITIZED = "prioritized"
    DELETED = "deleted"


class TaskEvent(Base):
    """Event log for task changes."""
    __tablename__ = "task_events"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    event_type = Column(Enum(TaskEventType), nullable=False)
    payload = Column(JSONB, nullable=True)  # JSON payload of the event
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    task = relationship("Task", back_populates="events")
