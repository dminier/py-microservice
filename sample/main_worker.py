from celery import Celery

from sample.application.bootstrap import Bootstrap

app: Celery = Bootstrap.build_worker(production=True)

if __name__ == "__main__":
    app.start()
