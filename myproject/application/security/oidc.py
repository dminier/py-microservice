import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from myproject.application.security.oidc_config import OIDC_CONFIG
from myproject.application.security.token import (
    JWTAccessToken,
    map_payload_to_jwt_access_token,
)

security = HTTPBearer()


def decode_jwt_token(token: str) -> JWTAccessToken:
    if OIDC_CONFIG is None:
        raise ValueError(
            "OIDC_CONFIG is None, check environment variable OIDC_CONFIGURATION_URL."
        )

    try:
        signing_key = OIDC_CONFIG.jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=OIDC_CONFIG.signing_algos,
            audience=OIDC_CONFIG.audience,
        )

        jwt_token_object: JWTAccessToken = map_payload_to_jwt_access_token(payload)
        logger.debug("JWT token decoded: {}", jwt_token_object)
        return jwt_token_object

    except jwt.ExpiredSignatureError as e:
        logger.debug("JWT expired token error: {}", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token has expired.",
        )
    except jwt.InvalidTokenError as e:
        logger.debug("JWT invalid token error: {}", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token is invalid.",
        )


def oidc_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> JWTAccessToken:
    token = credentials.credentials
    return decode_jwt_token(token)
