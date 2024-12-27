import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sample.application.bootstrap import Bootstrap

app: FastAPI = Bootstrap.create_app()
client = TestClient(app)


def _get_token():
    token_url = (
        "http://localhost:8024/realms/pymicroservice/protocol/openid-connect/token"
    )
    token_payload = {
        "grant_type": "password",
        "client_id": "myclient",
        "client_secret": "BtkZhTjSkOVgxRknWvZV6f0fQx26PkIH",
        "username": "test_user",
        "password": "test",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    response = requests.post(token_url, data=token_payload, headers=headers)
    response.raise_for_status()
    response_json = response.json()

    return response_json.get("access_token")


def test_protected():
    response = client.get("/api/v1/protected")
    assert response.status_code == 403

    access_token = _get_token()

    response = client.get(
        "/api/v1/protected", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    # get token from oidc service:
