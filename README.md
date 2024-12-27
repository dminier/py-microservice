# py-microservice

This repository serves as a comprehensive guide to the best practices for Python development within a microservices architecture.

# Code Structure

We have 2 main modules :

- `sample` : The sample module as an example of a simple microservice.
- `pymicroservice` : With all technical considerations needed for a microservice.

## Microservice Architecture with this repository

# Clean architecture or Hexagonal architecture or whatever architecture

Choose your own destiny. There is no one-size-fits-all solution. The most important principles are: maintaining consistency, aligning with the team's skills, and ensuring enjoyment in the work process.

Here, what we are looking it's common technical considerations that can be applied to all architectures.

For this example, we will use a custom kiss architecture, only for the sake of simplicity and ready to extends it with your own architecture.

# Packaging and Dependency Management

We use `uv` as a package manager. It's designed to be fast, reliable, and easy to use.

# Security

This project includes a basic security with OIDC and JWT. The main goal is to provide a simple example of how to secure your microservices.

## Configuration

Your environment variables should be stored in a `.env` file at the root of your project. This file should be added to your `.gitignore` file to prevent it from being committed to your repository (this is not done in this repository).

Here is an example with docker-compose and keycloak.

```bash
# OpenID configuration
# ------------------------------------------------------------------
OIDC_CONFIGURATION_URL=http://localhost:8024/realms/pymicroservice/.well-known/openid-configuration
# OIDC_AUDIENCE=account
```

## Securing a Route

Securing an endpoint with OIDC can be done as follows with `oidc_auth`.

```python
from fastapi import APIRouter, Depends, FastAPI

from pymicroservice.security.oidc import oidc_auth
from pymicroservice.security.token import JWTAccessToken

app = FastAPI()
router = APIRouter()


@router.get("/protected")
async def protected_route(access_token: JWTAccessToken = Depends(oidc_auth)):
    """
    Protected route example.
    """
    return {"message": "Authorized access", "JWTAccessToken": access_token}
```

`JWTAccessToken` is a Pydantic model that represents the JWT token. It is automatically populated by the `oidc_auth` dependency, according to the provided Bearer token and the OIDC configuration.

## Testing

An easy way to test the security of your routes is to use the `pytest` library. You can use the `pytest` fixtures provided in `pymicroservice.security.tests.fixtures` to mock the OIDC server and test the security of your routes.

```python
import datetime
import uuid
from datetime import timedelta
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from pymicroservice.security.token import JWTAccessToken
from sample.application.bootstrap import Bootstrap

app: FastAPI = Bootstrap.create_app()
client = TestClient(app)


def mock_decode_jwt_token(token: str):
    """
    Mock function to replace the real JWT decoding logic.
    """
    now = datetime.datetime.now()
    if token == "fake_token":
        return JWTAccessToken(
            iss="https://example.com",
            exp=int((now + timedelta(hours=1)).timestamp()),  # Expire in 1 hour
            aud="account",
            sub="user_12345",
            iat=int(now.timestamp()),
            jti=str(uuid.uuid4()),  # Generate unique token ID
            auth_time=str(int(now.timestamp())),
            acr="urn:mace:incommon:iap:silver",
            amr=["password"],
            extra_claims={"role": "admin", "department": "IT"},
        )


@patch(
    "pymicroservice.security.oidc.decode_jwt_token", side_effect=mock_decode_jwt_token
)
def test_protected(mock_decode_jwt_token):
    response = client.get("/api/v1/protected")
    assert response.status_code == 403

    response = client.get(
        "/api/v1/protected", headers={"Authorization": "Bearer fake_token"}
    )
    assert response.status_code == 200
```

you can find fully integrated tests in [tests.fully-integrated/user_endpoint_test.py](tests/fully-integrated/user_endpoint_test.py).

# Logging

We use `loguru` as a logging library. It is designed to be simple, efficient, and easy to use and most of all : it's colorful 😄

The difficulty is to have the same log format for `uvicorn` and `gunicorn`. We provide a simple solution in `pymicroservice.logging`.

You can easy switch level and output format with environment variables :

```bash
# LOGGER Configuration
# ------------------------------------------------------------------
# LOG_LEVEL=INFO
# LOG_JSON_OUTPUT=false
```

All you need in your code : use loguru.

# Production-Ready

## Run Uvicorn with Gunicorn

Here the `main.py`.

```python
import os

from gunicorn.app.base import BaseApplication

from pymicroservice.logger.logger_config import StubbedGunicornLogger
from sample.application.bootstrap import Bootstrap

WORKERS = int(os.environ.get("GUNICORN_WORKERS", "1"))
PORT = int(os.environ.get("GUNICORN_PORT", "8000"))


class StandaloneApplication(BaseApplication):
    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


if __name__ == "__main__":
    options = {
        "bind": f"0.0.0.0:{PORT}",
        "workers": WORKERS,
        "accesslog": "-",
        "errorlog": "-",
        "worker_class": "uvicorn.workers.UvicornWorker",
        "logger_class": StubbedGunicornLogger,
    }

    StandaloneApplication(Bootstrap.create_app(production=True), options).run()
```

and the corresponding environment variables :

```bash
# GUNICORN_WORKERS=1
# GUNICORN_PORT=8000
```

## liveness and readiness probes

There are two types of probes that can be used to monitor the health of your application: liveness and readiness probes. Liveness probes are used to determine if the application is running, while readiness probes are used to determine if the application is ready to serve traffic.

```python
from fastapi import APIRouter

router = APIRouter()


@router.get("/health/liveness", tags=["health"])
async def liveness_check():
    """
    Liveness check to monitor if the application is running.
    Returns 200 OK if the application is alive.

    deployment.yaml :

    livenessProbe:
      httpGet:
        path: /health/liveness
        port: 80
      initialDelaySeconds: 3
      periodSeconds: 10
    """
    return {"status": "alive"}


@router.get("/health/readiness", tags=["health"])
async def readiness_check():
    """
    Readiness check to monitor if the application is ready to serve traffic.
    Add checks for database connections, external services, etc., here.
    Returns 200 OK if the application is ready.

    deployment.yaml :

    readinessProbe:
        httpGet:
            path: /readiness
            port: 80
        initialDelaySeconds: 5
        periodSeconds: 5
    """
    # # Example: Add logic to verify database connection or other dependencies
    # db_connected = True  # Replace with actual check
    # if not db_connected:
    #     return {"status": "not ready"}, 503

    return {"status": "up"}
```

# References

- UV, Packaging and project manager : https://astral.sh/blog/uv
- UV, Usefull guide : https://medium.com/@gnetkov/start-using-uv-python-package-manager-for-better-dependency-management-183e7e428760
- Fastapi, Python web framework : https://fastapi.tiangolo.com/
- Loguru, Python logging library : https://github.com/Delgan/loguru
- Loguru, usefull uvicorn integration : https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
- vscode-python, very good pratices here : https://github.com/microsoft/vscode-python/tree/main/.vscode
- keycloak with usefull docker integration : https://github.com/little-pinecone/keycloak-in-docker
- PyJWT : https://pyjwt.readthedocs.io/en/latest/usage.html
- 12-Factor : https://12factor.net/, https://github.com/twelve-factor/twelve-factor

# Feature Roadmap

- Testing Strategies: Unit, integration, and end-to-end testing techniques for microservices.
- Task Scheduling: Techniques for scheduling and executing background tasks.
- Containerization: Dockerizing Python microservices with development and production configurations.
- CI/CD Pipelines: Guidelines for automating build, test, and deployment processes.
- Development Workflow: Best practices for developing with .devcontainer, VSCode, and Git.
