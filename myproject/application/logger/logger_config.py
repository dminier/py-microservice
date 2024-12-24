import inspect
import logging
import os
import sys
from dataclasses import dataclass

from loguru import logger

LOG_LEVEL = logging.getLevelName(os.environ.get("LOG_LEVEL", "DEBUG"))


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


@dataclass
class Config:
    level: str
    format: str
    json: bool


class LoggerConfig:
    @classmethod
    def configure(cls):
        config: Config = cls.load_config()

        cls._configure(config)

    @classmethod
    def _configure(cls, config: Config):
        # intercept everything at the root logger
        logging.root.handlers = [InterceptHandler()]
        logging.root.setLevel(config.level)

        # remove every other logger's handlers
        # and propagate to root logger
        for name in logging.root.manager.loggerDict.keys():
            logging.getLogger(name).handlers = []
            logging.getLogger(name).propagate = True

        # configure loguru
        logger.configure(handlers=[{"sink": sys.stdout, "serialize": config.json}])

    @classmethod
    def load_config(cls) -> Config:
        level = os.getenv("LOG_LEVEL", "INFO")
        format = os.getenv("LOG_FORMAT", None)
        json = True if os.environ.get("LOG_JSON", "0") == "1" else False
        return Config(level, format, json)
