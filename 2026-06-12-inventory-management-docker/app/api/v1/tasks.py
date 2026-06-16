from fastapi import APIRouter, Depends
from celery.result import AsyncResult
from celery_app import celery_app
from app.core.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/{task_id}", summary="Check Task Status (Celery)")
def get_task_status(
    task_id: str,
    current_user=Depends(get_current_user),
):
    """
    (Celery) Global endpoint to check the status and result of ANY background task.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    result = {
        "task_id": task_id,
        "status": task_result.status,
        "result": task_result.result if task_result.ready() else None
    }
    return result
