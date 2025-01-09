from fastapi import FastAPI
from fastapi.testclient import TestClient

from sample.application.bootstrap import Bootstrap

app: FastAPI = Bootstrap.build_api()
client = TestClient(app)


def test_health_liveness():
    response = client.get("/health/liveness")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_health_readiness():
    response = client.get("/health/readiness")
    assert response.status_code == 200
    assert response.json() == {"status": "up"}
