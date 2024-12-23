from fastapi import FastAPI
from loguru import logger

from myproject.application import health_endpoint, user_endpoint


class Bootstrap:
    API_ROUTE_PREFIX: str = "/api"

    # Liste des endpoints à configurer
    ENDPOINTS = [user_endpoint, health_endpoint]

    @staticmethod
    def create_app() -> FastAPI:
        logger.debug("Creating FastAPI app")
        # Initialisation de l'application
        app = FastAPI()

        # Configuration des dépendances
        # Bootstrap.setup_dependency_injection()

        # Configuration des routes
        Bootstrap.setup_routers(app)

        return app

    @staticmethod
    def setup_routers(app: FastAPI):
        logger.debug("Setting up routers")
        for endpoint in Bootstrap.ENDPOINTS:
            # app.include_router(endpoint.router, prefix=Bootstrap.API_ROUTE_PREFIX)
            app.include_router(endpoint.router)

    # @staticmethod
    # def setup_dependency_injection():
    #     logger.debug("Setting up dependency injection")
    #     # Initialisation des conteneurs
    #     domain_container = VirtualStaffContainer()

    #     # Câblage des modules avec les conteneurs
    #     domain_container.wire(modules=ApplicationBootstrap.ENDPOINTS)
