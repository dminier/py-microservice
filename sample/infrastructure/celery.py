from celery import Celery
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

logger.info("🔧 Setting up Celery")


class CeleryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CELERY_", validate_default=False)
    broker_url: str = "redis://localhost:6379"
    result_backend: str = "redis://localhost:6379"


CELERY_CONFIG = CeleryConfig()


WORKER = Celery("sample_app", broker=CELERY_CONFIG.broker_url)
WORKER.conf.update(
    broker_url=CELERY_CONFIG.broker_url,
    result_backend=CELERY_CONFIG.result_backend,
)

# This snippet is used to autodiscover tasks from the application, here we are using the user module as an example
