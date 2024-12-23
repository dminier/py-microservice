import os
from dataclasses import dataclass

import jwt
import requests
from loguru import logger


@dataclass
class OidcConfig:
    signing_algos: list[str]
    jwks_uri: str
    jwks_client: jwt.PyJWKClient
    audience: str


def _load_oidc_config() -> OidcConfig:
    oidc_config_url = os.getenv("OIDC_CONFIGURATION_URL", None)

    if oidc_config_url is None:
        logger.warning(
            "OIDC_CONFIGURATION_URL not found in environment variables. No security check will be performed."
        )
        return None

    audience = os.getenv("OIDC_AUDIENCE", None)

    if audience is None:
        raise EnvironmentError("OIDC_AUDIENCE not found in environment variables.")

    oidc_config = requests.get(oidc_config_url, timeout=10).json()

    signing_algos = oidc_config.get("id_token_signing_alg_values_supported", None)

    if signing_algos is None:
        raise ValueError(
            f"id_token_signing_alg_values_supported not found in OIDC configuration, check environment variable OIDC_CONFIGURATION_URL=f{oidc_config_url}."
        )
    jwks_uri = oidc_config.get("jwks_uri", None)

    if jwks_uri is None:
        raise ValueError(
            f"jwks_uri not found in OIDC configuration, check environment variable OIDC_CONFIGURATION_URL=f{oidc_config_url}."
        )

    jwks_client = jwt.PyJWKClient(jwks_uri)
    return OidcConfig(signing_algos, jwks_uri, jwks_client, audience)


OIDC_CONFIG: OidcConfig = _load_oidc_config()
