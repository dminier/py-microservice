import inspect
import logging
import sys

from gunicorn.glogging import Logger
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggerConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOG_", validate_default=False)
    level: str = "INFO"
    format: str = ""
    json_output: bool = False


LOGGER_CONFIG = LoggerConfig()


class StubbedGunicornLogger(Logger):
    def setup(self, cfg):
        handler = logging.NullHandler()
        self.error_logger = logging.getLogger("gunicorn.error")
        self.error_logger.addHandler(handler)
        self.access_logger = logging.getLogger("gunicorn.access")
        self.access_logger.addHandler(handler)
        self.error_logger.setLevel(LOGGER_CONFIG.level)
        self.access_logger.setLevel(LOGGER_CONFIG.level)


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)


class LoggerConfig:
    @classmethod
    def configure(cls, production: bool):
        logging.root.setLevel(LOGGER_CONFIG.level)
        if production:
            cls._setup_guvicorn()
        else:
            cls._setup_uvicorn_only()

    @classmethod
    def _setup_guvicorn(cls):
        intercept_handler = InterceptHandler()
        logging.root.setLevel(LOGGER_CONFIG.level)

        seen = set()
        for name in [
            *logging.root.manager.loggerDict.keys(),
            "gunicorn",
            "gunicorn.access",
            "gunicorn.error",
            "uvicorn",
            "uvicorn.access",
            "uvicorn.error",
        ]:
            if name not in seen:
                seen.add(name.split(".")[0])
                logging.getLogger(name).handlers = [intercept_handler]

        logger.configure(
            handlers=[{"sink": sys.stdout, "serialize": LOGGER_CONFIG.json_output}]
        )

    @classmethod
    def _setup_uvicorn_only(cls):
        # intercept everything at the root logger
        logging.root.handlers = [InterceptHandler()]
        logging.root.setLevel(LOGGER_CONFIG.level)

        # remove every other logger's handlers
        # and propagate to root logger
        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

        # configure loguru
        logger.configure(
            handlers=[{"sink": sys.stdout, "serialize": LOGGER_CONFIG.json_output}]
        )
