from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class JWTAccessToken:
    iss: str
    exp: int
    aud: str
    sub: str
    iat: int
    jti: str

    # Optional fields for authentication information
    auth_time: Optional[str] = None
    acr: Optional[str] = None
    amr: Optional[List[str]] = field(default_factory=list)

    extra_claims: Dict[str, Any] = field(
        default_factory=dict
    )  # Stores claims not in the spec https://datatracker.ietf.org/doc/rfc9068/


def map_payload_to_jwt_access_token(payload: dict) -> JWTAccessToken:
    standard_fields = {
        "iss",
        "exp",
        "aud",
        "sub",
        "iat",
        "jti",
        "auth_time",
        "acr",
        "amr",
    }

    standard_data = {field: payload.get(field) for field in standard_fields}

    extra_claims = {
        key: value for key, value in payload.items() if key not in standard_fields
    }

    return JWTAccessToken(
        **{key: value for key, value in standard_data.items() if value is not None},
        extra_claims=extra_claims,
    )
