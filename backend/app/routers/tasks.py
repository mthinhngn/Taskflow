import logging
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import User
from app.schemas import TaskCreate, TaskUpdate, TaskResponse
from app.services.tasks import (
    create_task,
    get_task,
    list_tasks,
    update_task,
    delete_task,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task."""
    try:
        db_task = create_task(db, task_data, current_user.id)
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("", response_model=dict)
async def list_tasks_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, alias="status"),
    project_id: Optional[int] = None,
    due_from: Optional[datetime] = None,
    due_to: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List tasks with filters and pagination."""
    tasks, total = list_tasks(
        db,
        current_user.id,
        status=status_filter,
        project_id=project_id,
        due_from=due_from,
        due_to=due_to,
        skip=skip,
        limit=limit,
    )
    return {
        "items": [TaskResponse.from_orm(t) for t in tasks],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a task by ID."""
    db_task = get_task(db, task_id, current_user.id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a task."""
    db_task = update_task(db, task_id, current_user.id, task_data)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a task."""
    success = delete_task(db, task_id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
