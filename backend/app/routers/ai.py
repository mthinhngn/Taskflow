import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import User, Task
from app.schemas import PrioritizationRequest, PrioritizationResponse, TaskForPrioritization
from app.services.ai import prioritize_tasks

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/prioritize", response_model=PrioritizationResponse)
async def prioritize_endpoint(
    request: PrioritizationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Prioritize a list of tasks using AI (OpenAI) or rule-based fallback.
    
    Input: List of tasks with metadata (title, due_at, estimated_minutes, importance)
    Output: Prioritized results with scores/rationales and a daily plan
    """
    try:
        results, plan = prioritize_tasks(request.tasks)
        
        logger.info(f"Prioritized {len(request.tasks)} tasks for user {current_user.id}")
        
        return PrioritizationResponse(results=results, plan=plan)
    
    except Exception as e:
        logger.error(f"Prioritization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prioritization failed"
        )


@router.post("/prioritize-saved")
async def prioritize_saved_tasks(
    project_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Prioritize tasks from the database (saved tasks).
    """
    query = db.query(Task).filter(Task.user_id == current_user.id, Task.status != "done")
    if project_id:
        query = query.filter(Task.project_id == project_id)
    
    tasks = query.all()
    if not tasks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No tasks found to prioritize"
        )

    # Convert DB tasks to prioritization request format
    task_inputs = [
        TaskForPrioritization(
            title=task.title,
            description=task.description,
            due_at=task.due_at,
            estimated_minutes=task.estimated_minutes,
            importance=task.priority,
        )
        for task in tasks
    ]

    results, plan = prioritize_tasks(task_inputs)
    
    # Update AI scores in database
    for result in results:
        task = next((t for t in tasks if t.title == result.title), None)
        if task:
            task.ai_score = result.score
    
    db.commit()
    logger.info(f"Prioritized {len(tasks)} saved tasks for user {current_user.id}")

    return {
        "results": results,
        "plan": plan,
    }
