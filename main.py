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
