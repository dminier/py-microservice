import logging
import os
import sys

from dotenv import load_dotenv
from loguru import logger
from uvicorn import Config, Server

log_level = os.getenv("LOGURU_LEVEL", "ERROR")  # Par défaut, le niveau est INFO

logger.remove()
logger.add(
    sink=sys.stderr,
    level=log_level,
)


# Intégrer Loguru avec le système de logging Python
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Convertir les logs standard en logs Loguru
        loguru_level = (
            logger.level(record.levelname).name
            if record.levelname in logger._levels
            else record.levelno
        )
        logger.log(loguru_level, record.getMessage())


# Rediriger les logs vers Loguru
logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)
