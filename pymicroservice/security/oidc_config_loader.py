import os
from dataclasses import dataclass
from typing import Optional

import jwt
import requests
from loguru import logger


@dataclass
class OidcConfig:
    signing_algos: list[str]
    jwks_uri: str
    jwks_client: jwt.PyJWKClient
    audience: str


class OidcConfigLoader:
    """
    A class responsible for loading and managing OIDC configuration.
    """

    def __init__(
        self,
        config_url_env: str = "OIDC_CONFIGURATION_URL",
        audience_env: str = "OIDC_AUDIENCE",
    ):
        """
        Initialize the OIDC configuration loader.

        :param config_url_env: Name of the environment variable containing the OIDC configuration URL.
        :param audience_env: Name of the environment variable containing the audience.
        """
        self.config_url_env = config_url_env
        self.audience_env = audience_env
        self.config: Optional[OidcConfig] = None

    def load(self) -> Optional[OidcConfig]:
        """
        Load the OIDC configuration.

        :return: An instance of OidcConfig or None if the configuration is invalid.
        """
        oidc_config_url = os.getenv(self.config_url_env)

        if not oidc_config_url:
            logger.warning(
                f"{self.config_url_env} not found in environment variables. No security checks will be performed."
            )
            return None

        audience = os.getenv(self.audience_env, "account")

        if not audience:
            raise EnvironmentError(
                f"{self.audience_env} not found in environment variables."
            )

        oidc_config = self._fetch_oidc_config(oidc_config_url)

        signing_algos = oidc_config.get("id_token_signing_alg_values_supported")
        if not signing_algos:
            raise ValueError(
                f"'id_token_signing_alg_values_supported' not found in OIDC configuration. "
                f"Check environment variable {self.config_url_env}={oidc_config_url}."
            )

        jwks_uri = oidc_config.get("jwks_uri")
        if not jwks_uri:
            raise ValueError(
                f"'jwks_uri' not found in OIDC configuration. "
                f"Check environment variable {self.config_url_env}={oidc_config_url}."
            )

        jwks_client = jwt.PyJWKClient(jwks_uri)
        self.config = OidcConfig(signing_algos, jwks_uri, jwks_client, audience)

        logger.debug("OIDC configuration loaded: {}", self.config)
        return self.config

    def _fetch_oidc_config(self, url: str) -> dict:
        """
        Fetch the OIDC configuration from a given URL.

        :param url: The OIDC configuration URL.
        :return: A dictionary containing the OIDC configuration.
        """
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch OIDC configuration from {url}: {e}")
            raise

    def get_config(self) -> Optional[OidcConfig]:
        """
        Retrieve the loaded configuration, if any.

        :return: An OidcConfig instance or None.
        """
        return self.config
