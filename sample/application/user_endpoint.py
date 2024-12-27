from fastapi import APIRouter, Depends, FastAPI

from pymicroservice.security.oidc import oidc_auth
from pymicroservice.security.token import JWTAccessToken

app = FastAPI()
router = APIRouter()


@router.get("/protected")
def protected_route(access_token: JWTAccessToken = Depends(oidc_auth)):
    """
    Protected route example.
    """
    return {"message": "Authorized access", "JWTAccessToken": access_token}


@router.get("/public")
def public_route():
    """
    Public route example.
    """
    return {"message": "Welcome in a public place"}
