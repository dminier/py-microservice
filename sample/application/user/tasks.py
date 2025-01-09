from time import sleep

from loguru import logger

# from sample.main_worker import CELERY_APP
from sample.domain.user_model import UserTask
from sample.infrastructure.celery import WORKER


@WORKER.task
def user_sample_task(user: UserTask) -> str:
    """
    Executes a sample task that simulates a long-running operation.

    Args:
        task_name (str): The name of the task to be executed.

    Returns:
        str: A message indicating that the task has been completed.
    """
    logger.debug(f"Task {user.name} started")
    sleep(5)  # Simulate a long-running operation
    logger.debug(f"Task {user.name} completed")
    return f"Task completed: {user.name}"
