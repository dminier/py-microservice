import os

from fastapi import FastAPI
from loguru import logger

from myproject.application import health_endpoint, user_endpoint
from myproject.application.logger.logger_config import LoggerConfig

API_ROUTE_PREFIX: str = os.getenv("API_ROUTE_PREFIX", "/api/v1")


class Bootstrap:
    # List of endpoints
    API_ENDPOINTS = [user_endpoint]

    @classmethod
    def create_app(cls, production: bool = False) -> FastAPI:
        LoggerConfig.configure(production)

        logger.info("🌟 Creating FastAPI app")
        app = FastAPI(debug=False)
        # IOC
        # Bootstrap.setup_dependency_injection()

        # Router setup
        logger.info("🔧 Setting up routers")
        cls._setup_routers(logger, app)
        logger.info("✅ Boostrap finish")
        return app

    @classmethod
    def _setup_routers(cls, logger, app: FastAPI):
        for endpoint in Bootstrap.API_ENDPOINTS:
            app.include_router(endpoint.router, prefix=API_ROUTE_PREFIX)

        app.include_router(health_endpoint.router)

    # @staticmethod
    # def setup_dependency_injection():
    #     logger.debug("Setting up dependency injection")
    #     # Initialisation des conteneurs
    #     domain_container = VirtualStaffContainer()

    #     # Câblage des modules avec les conteneurs
    #     domain_container.wire(modules=ApplicationBootstrap.ENDPOINTS)
