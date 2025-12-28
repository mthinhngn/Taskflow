import logging
from typing import Optional, List
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import Task, TaskEvent, TaskEventType, Project
from app.schemas import TaskCreate, TaskUpdate

logger = logging.getLogger(__name__)


def create_task(db: Session, task_create: TaskCreate, user_id: int) -> Task:
    """Create a new task."""
    # Verify project exists and belongs to user
    project = db.query(Project).filter(
        Project.id == task_create.project_id,
        Project.user_id == user_id
    ).first()
    
    if not project:
        raise ValueError(f"Project {task_create.project_id} not found or not owned by user")

    db_task = Task(
        **task_create.dict(),
        user_id=user_id
    )
    db.add(db_task)
    db.flush()

    # Log event
    event = TaskEvent(
        task_id=db_task.id,
        event_type=TaskEventType.CREATED,
        payload={"status": db_task.status.value}
    )
    db.add(event)
    db.commit()
    db.refresh(db_task)

    logger.info(f"Task {db_task.id} created for user {user_id}")
    return db_task


def get_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """Get a task by ID (check ownership)."""
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()


def list_tasks(
    db: Session,
    user_id: int,
    status: Optional[str] = None,
    project_id: Optional[int] = None,
    due_from: Optional[datetime] = None,
    due_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List[Task], int]:
    """List tasks for a user with filters and pagination."""
    query = db.query(Task).filter(Task.user_id == user_id)

    if status:
        query = query.filter(Task.status == status)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if due_from:
        query = query.filter(Task.due_at >= due_from)
    if due_to:
        query = query.filter(Task.due_at <= due_to)

    total = query.count()
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    return tasks, total


def update_task(db: Session, task_id: int, user_id: int, task_update: TaskUpdate) -> Optional[Task]:
    """Update a task."""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None

    update_data = task_update.dict(exclude_unset=True)

    # Track status changes
    old_status = db_task.status
    for field, value in update_data.items():
        setattr(db_task, field, value)

    if "status" in update_data and update_data["status"] != old_status:
        event = TaskEvent(
            task_id=task_id,
            event_type=TaskEventType.STATUS_CHANGED,
            payload={"from": old_status.value, "to": update_data["status"].value}
        )
        db.add(event)

    if update_data:
        event = TaskEvent(
            task_id=task_id,
            event_type=TaskEventType.UPDATED,
            payload=update_data
        )
        db.add(event)

    db.commit()
    db.refresh(db_task)
    logger.info(f"Task {task_id} updated for user {user_id}")
    return db_task


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """Delete a task."""
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    logger.info(f"Task {task_id} deleted for user {user_id}")
    return True
