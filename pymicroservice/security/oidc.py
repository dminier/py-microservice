from asyncio import Lock

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger

from pymicroservice.security.oidc_config_loader import OidcConfig, OidcConfigLoader
from pymicroservice.security.token import (
    JWTAccessToken,
    map_payload_to_jwt_access_token,
)

SECURITY_BEARER = HTTPBearer()


class OidcConfigSingleton:
    _instance = None
    _lock = Lock()

    @classmethod
    async def get_instance(cls) -> OidcConfig:
        if cls._instance is None:
            async with cls._lock:  # Ensure thread safety
                if cls._instance is None:
                    loader = OidcConfigLoader()
                    cls._instance = loader.load()
        return cls._instance


async def get_oidc_config() -> OidcConfig:
    return await OidcConfigSingleton.get_instance()


def decode_jwt_token(
    token: str,
    oidc_config: OidcConfig,
) -> JWTAccessToken:
    try:
        signing_key = oidc_config.jwks_client.get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=oidc_config.signing_algos,
            audience=oidc_config.audience,
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


async def oidc_auth(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_BEARER),
    oidc_config: OidcConfig = Depends(get_oidc_config),
) -> JWTAccessToken:
    token = credentials.credentials
    return decode_jwt_token(token, oidc_config)
