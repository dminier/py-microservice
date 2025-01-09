import os
from time import sleep

import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient

from sample.application.bootstrap import Bootstrap

app: FastAPI = Bootstrap.build_api()
client = TestClient(app)


def _get_token():
    token_url = f"{os.getenv("TEST_KEYCLOAK_URL")}/realms/pymicroservice/protocol/openid-connect/token"
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
    # without token, we should get a 403
    endpoint = "/api/v1/user/protected"
    response = client.get(endpoint)
    assert response.status_code == 403

    # with token, we should get a 200
    access_token = _get_token()
    response = client.get(endpoint, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


def test_public():
    endpoint = "/api/v1/user/public"
    # without token, we should get a 200
    response = client.get(endpoint)
    assert response.status_code == 200

    # with token, we should get a 200 too
    access_token = _get_token()
    response = client.get(endpoint, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200


def test_task():
    # create a task
    response = client.post("/api/v1/user/task", json={"name": "test_task"})

    assert response.status_code == 200
    created_task_data = response.json()
    assert created_task_data.get("status") == "Task submitted"

    # check task status
    query = f"/api/v1/worker/task/{created_task_data.get('task_id')}"

    response = client.get(query)
    assert response.status_code == 200
    status_task = response.json()
    assert status_task.get("status") == "PENDING"

    # we need to wait for the task to be completed
    sleep(10)
    response = client.get(query)
    assert response.status_code == 200
    status_task = response.json()
    assert status_task.get("status") == "SUCCESS"
