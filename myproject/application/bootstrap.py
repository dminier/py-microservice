import os

from fastapi import FastAPI
from loguru import logger

from myproject.application import health_endpoint, user_endpoint
from myproject.application.logger.logger_config import LoggerConfig

API_ROUTE_PREFIX: str = os.getenv("API_ROUTE_PREFIX", "/api/v1")


class Bootstrap:
    # List of endpoints
    API_ENDPOINTS = [user_endpoint]

    @staticmethod
    def create_app() -> FastAPI:
        logger.debug("Creating FastAPI app")
        LoggerConfig.configure()
        app = FastAPI(debug=False)

        # IOC
        # Bootstrap.setup_dependency_injection()

        # Router setup
        Bootstrap.setup_routers(app)

        return app

    @staticmethod
    def setup_routers(app: FastAPI):
        logger.debug("Setting up routers")
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
