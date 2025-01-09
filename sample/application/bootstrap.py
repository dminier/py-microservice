import os

from celery import Celery
from fastapi import FastAPI
from loguru import logger

from pymicroservice.kombu.register_pydantic import register_pydantic_types
from pymicroservice.logger.logger_config import LoggerConfig
from sample.application.health import health_endpoint
from sample.application.user import user_endpoint
from sample.application.worker import worker_endpoint
from sample.domain.user_model import UserTask
from sample.infrastructure.celery import WORKER

API_ROUTE_PREFIX: str = os.getenv("API_ROUTE_PREFIX", "/api/v1")


class Bootstrap:
    # List of endpoints
    API_ENDPOINTS = [user_endpoint, worker_endpoint]
    WORKER_PACKAGES = ["sample.application.user"]
    WORKER_PYDANTIC_MODELS = [UserTask]

    @classmethod
    def build_api(cls, production: bool = False) -> FastAPI:
        logger.info("🚀 Creating API")
        LoggerConfig.configure(production)
        app = FastAPI(debug=False)
        cls._setup_routers(logger, app)
        cls._setup_workers()
        return app

    @classmethod
    def build_worker(cls, production: bool = False) -> Celery:
        logger.info("🚀 Creating Worker")
        LoggerConfig.configure(production)
        cls._setup_workers()
        return WORKER

    @classmethod
    def _setup_routers(cls, logger, app: FastAPI):
        app.include_router(health_endpoint.router)

        for endpoint in Bootstrap.API_ENDPOINTS:
            app.include_router(endpoint.router, prefix=API_ROUTE_PREFIX)

        app.include_router(endpoint.router)

    @classmethod
    def _setup_workers(cls):
        WORKER.autodiscover_tasks(Bootstrap.WORKER_PACKAGES, force=True)
        register_pydantic_types(Bootstrap.WORKER_PYDANTIC_MODELS)
