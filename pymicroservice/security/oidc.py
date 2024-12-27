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


class OidcConfigManager:
    """
    Singleton manager for OIDC_CONFIG, allowing easy mocking and reloading.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config = None
        return cls._instance

    def load(self):
        """
        Load the OIDC configuration using the OidcConfigLoader.
        """
        loader = OidcConfigLoader()
        self._config = loader.load()

    def set_config(self, config: OidcConfig):
        """
        Set a custom OIDC configuration, useful for mocking in tests.
        """
        self._config = config

    def get_config(self) -> OidcConfig:
        """
        Get the current OIDC configuration. Raise an error if not set.
        """
        if self._config is None:
            raise ValueError("OIDC_CONFIG is not set. Ensure it is loaded or mocked.")
        return self._config


def decode_jwt_token(token: str) -> JWTAccessToken:
    OIDC_CONFIG_MANAGER = OidcConfigManager()
    OIDC_CONFIG_MANAGER.load()

    oidc_config = OIDC_CONFIG_MANAGER.get_config()

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


def oidc_auth(
    credentials: HTTPAuthorizationCredentials = Depends(SECURITY_BEARER),
) -> JWTAccessToken:
    token = credentials.credentials
    return decode_jwt_token(token)
