from fastapi import APIRouter, Depends, FastAPI

from myproject.application.security.oidc import oidc_auth

app = FastAPI()
router = APIRouter()


@router.get("/protected")
def protected_route(payload: dict = Depends(oidc_auth)):
    """
    Exemple de route protégée :
    - On récupère directement le payload décodé dans la dépendance.
    """
    return {"message": "Authorized access", "payload": payload}


@router.get("/public")
def public_route():
    """
    Exemple de route publique.
    """
    return {"message": "Welcome in a public place"}
