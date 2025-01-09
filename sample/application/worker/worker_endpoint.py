from fastapi import APIRouter

from sample.infrastructure.celery import WORKER

router = APIRouter()


@router.get("/worker/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a Celery task by task_id.
    """
    task_result = WORKER.AsyncResult(task_id)
    if task_result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": task_result.state,
            "result": task_result.result,
        }
    return {"task_id": task_id, "status": task_result.state}
