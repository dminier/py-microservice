from fastapi import APIRouter, Depends

from pymicroservice.security.oidc import oidc_auth
from pymicroservice.security.token import JWTAccessToken
from sample.application.user.tasks import user_sample_task
from sample.domain.user_model import UserTask

router = APIRouter()

oidc_auth_dependency = Depends(oidc_auth)


@router.get("/user/protected")
async def protected_route(access_token: JWTAccessToken = oidc_auth_dependency):
    """
    Protected route example.
    """
    return {"message": "Authorized access", "JWTAccessToken": access_token}


@router.get("/user/public")
async def public_route():
    """
    Public route example.
    """
    return {"message": "Welcome in a public place"}


@router.post("/user/task")
async def run_sample_task(user: UserTask):
    """
    Public route example.
    """
    task = user_sample_task.delay(user)
    return {"task_id": task.id, "status": "Task submitted"}
