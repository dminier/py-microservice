import datetime
import uuid
from datetime import timedelta
from unittest.mock import patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from pymicroservice.security.token import JWTAccessToken
from sample.application.bootstrap import Bootstrap

app: FastAPI = Bootstrap.build_api()
client = TestClient(app)


def mock_decode_jwt_token(token: str, oidc_config):
    """
    Mock function to replace the real JWT decoding logic.
    """
    now = datetime.datetime.now()
    if token == "fake_token":
        return JWTAccessToken(
            iss="https://example.com",
            exp=int((now + timedelta(hours=1)).timestamp()),  # Expire in 1 hour
            aud="account",
            sub="user_12345",
            iat=int(now.timestamp()),
            jti=str(uuid.uuid4()),  # Generate unique token ID
            auth_time=str(int(now.timestamp())),
            acr="urn:mace:incommon:iap:silver",
            amr=["password"],
            extra_claims={"role": "admin", "department": "IT"},
        )


@patch("pymicroservice.security.oidc.decode_jwt_token", side_effect=mock_decode_jwt_token)
def test_protected(mock_decode_jwt_token):
    query = "/api/v1/user/protected"
    response = client.get(query)
    assert response.status_code == 403

    response = client.get(query, headers={"Authorization": "Bearer fake_token"})
    assert response.status_code == 200
