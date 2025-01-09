# py-microservice

This repository serves as a template for building Python microservices with FastAPI and Celery. The goal is to provide technical features usually needed.

# Code Structure

We have 2 main modules :

- `sample` : The sample module as an example of a simple microservice.
- `pymicroservice` : With all technical considerations needed for a microservice.

## Microservice Architecture with this repository

# Clean architecture or Hexagonal architecture or whatever architecture

Choose,there is no one-size-fits-all solution. The most important principles are: maintaining consistency, aligning with the team's skills, and ensuring enjoyment in the work process.

Here, what we are looking it's common technical considerations that can be applied to all architectures.

For this example, we will use a custom kiss architecture, only for the sake of simplicity and ready to extends it with your own architecture.

# Packaging and Dependency Management

We use `uv` as a package manager. It's designed to be fast, reliable, and easy to use.

# Configuration

Environment variables are used to configure the application.

It's easy and readable.

# Bootstrapping and production ready scripts

## Bootstrapping

A good pratice is to use a bootstrapping script to start your application. Here a sample : [boostrap.py](sample/application/bootstrap.py)

All the glue code can be easily added here. We have an Api and a Worker in this example, so we have 2 bootstrapping functions.

## Production-Ready

### Run API : Uvicorn with Gunicorn

Here the main file : [main_api](sample/main_api.py)

and the corresponding environment variables :

```bash
# GUNICORN_WORKERS=1
# GUNICORN_PORT=8000
```

### Run Worker

Here the main file : [main_worker](sample/main_worker.py)

and the corresponding environment variables :

```bash
# WORKER Configuration
# ------------------------------------------------------------------
# Default : CELERY_BROKER_URL=redis://localhost:6379/0
# Default : CELERY_RESULT_BACKEND=redis://localhost:6379
```

**note :** this configuration is used by api and worker

### liveness and readiness probes

#### API

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

#### Worker

To check the worker, we can use the following command :

```bash
celery inspect ping -d celery@$(hostname) | grep -q OK
```

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

router = APIRouter()


@router.get("/protected")
async def protected_route(access_token: JWTAccessToken = Depends(oidc_auth)):
    """
    Protected route example.
    """
    return {"message": "Authorized access", "JWTAccessToken": access_token}
```

`JWTAccessToken` is a Pydantic model that represents the JWT token. It is automatically populated by the `oidc_auth` dependency, according to the provided Bearer token and the OIDC configuration.

## How to test a route that is secured with OIDC?

### Unit testing

One way to do it is to mock the function `pymicroservice.security.oidc.decode_jwt_token`. This function use the OIDC configuration to decode the token and verify the signature. Here, you can find a sample [user_enpoint_test.py](tests/unit/user_enpoint_test.py).

### Fully integrated testing

Rarely implemented, it's possible to test the route with a real keycloak server. For this projet, it's usefull. The main pain point for a real microservice is to configure a client able to allow a `grant_type=password`, and this is not recommended (in production).

We need to run `docker compose up -d` to start the keycloak server.

Here a sample to test : [tests.fully-integrated/user_endpoint_test.py](tests/fully-integrated/user_endpoint_test.py).

An other way, with a simple script [tests/usefull_authenticated_test.sh](tests/usefull_authenticated_test.sh)

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

# Worker Celery, running asynchrone tasks in background

## Dockerize Celery

### Build image and deploy

As you can see : the same docker image is used for the worker and the api but with different entrypoints.

```yaml
services:
  sample-api:
    build: .
    # ...
    command: >
      python sample/main_api.py
    # ...

  sample-worker:
    build: .
    # ...
    command: >
      celery -A sample.main_worker worker --pool=solo --loglevel=info
    # ...
```

## Add tasks and pass pydantic models in arguments

Bootstrapping script have to be updated to add tasks and pass pydantic models in arguments.

```python
    # register modules with "tasks.py" files
    WORKER_PACKAGES = ["sample.application.user"]
    # Add pydantic models here to be used in tasks
    WORKER_PYDANTIC_MODELS = [UserTask]
```

## Task

The name of the file is important : [tasks.py](sample/application/user/tasks.py)

```python
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

```

## Call a task

Here in [user_endpoint.py](sample/application/user/user_endpoint.py)

```python
from fastapi import APIRouter, Depends, FastAPI

from pymicroservice.security.oidc import oidc_auth
from pymicroservice.security.token import JWTAccessToken
from sample.application.user.tasks import user_sample_task
from sample.domain.user_model import UserTask

router = APIRouter()

# ...

@router.post("/user/task")
async def run_sample_task(user: UserTask):
    """
    Task call
    """
    task = user_sample_task.delay(user)
    return {"task_id": task.id, "status": "Task submitted"}

```

## Status of a task

It's usefull to have a route to check the status of a task, here the code : [worker_endpoint.py](sample/application/worker/worker_endpoint.py)

```python
from fastapi import APIRouter

from sample.infrastructure.celery import WORKER

router = APIRouter()


@router.get("/worker/task/{task_id}")
async def get_task_status(task_id: str):
    """
    Get the status of a Celery task by task_id.
    """
    task_result = WORKER.AsyncResult(task_id)
    if task_result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": task_result.state,
            "result": task_result.result,
        }
    return {"task_id": task_id, "status": task_result.state}
```

## flower : monitoring celery

Flower is a web based tool for monitoring and administrating Celery clusters. You can use it to view tasks, workers, and queues.

```yaml
flower:
  image: mher/flower
  command: ["celery", "--broker=redis://redis:6379/0", "flower"]
  ports:
    - "5555:5555"
  depends_on:
    - redis
```

# References

- UV, Packaging and project manager : https://astral.sh/blog/uv
- UV, Usefull guide : https://medium.com/@gnetkov/start-using-uv-python-package-manager-for-better-dependency-management-183e7e428760
- UV, split sample and pymicroservice with dependency groups : https://docs.astral.sh/uv/concepts/projects/dependencies/#dependency-groups
- Fastapi, Python web framework : https://fastapi.tiangolo.com/
- Loguru, Python logging library : https://github.com/Delgan/loguru
- Loguru, usefull uvicorn integration : https://pawamoy.github.io/posts/unify-logging-for-a-gunicorn-uvicorn-app/
- vscode-python, very good pratices here : https://github.com/microsoft/vscode-python/tree/main/.vscode
- keycloak with usefull docker integration : https://github.com/little-pinecone/keycloak-in-docker
- PyJWT : https://pyjwt.readthedocs.io/en/latest/usage.html
- 12-Factor : https://12factor.net/, https://github.com/twelve-factor/twelve-factor
- Celery serialization : https://benninger.ca/posts/celery-serializer-pydantic/
- Celery health check : https://github.com/celery/celery/issues/4079

# Feature Roadmap

- Testing Strategies: Unit, integration, and end-to-end testing techniques for microservices.
- Containerization: Dockerizing Python microservices with development and production configurations.
- CI/CD Pipelines: Guidelines for automating build, test, and deployment processes.
- Development Workflow: Best practices for developing with .devcontainer, VSCode, and Git.
