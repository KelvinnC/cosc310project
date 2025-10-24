import pytest
import asyncio
from fastapi import HTTPException, Request
import jwt
import os
from datetime import datetime, timedelta, timezone
from app.middleware.auth_middleware import jwt_auth_dependency

JWT_SECRET = os.getenv("JWT_SECRET")

def make_request_with_token(token: str | None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    scope = {"type": "http", "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()]}
    return Request(scope)


def create_token(payload: dict, expired=False):
    exp = (
        datetime.now(timezone.utc) - timedelta(seconds=10)
        if expired
        else datetime.now(timezone.utc) + timedelta(minutes=5)
    )
    return jwt.encode({**payload, "exp": exp}, JWT_SECRET, algorithm="HS256")


def test_missing_header():
    request = make_request_with_token(None)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(jwt_auth_dependency(request))
    assert exc.value.status_code == 401
    assert exc.value.detail == "Access Token Missing"


def test_valid_token():
    token = create_token({"user_id": "123"})
    request = make_request_with_token(token)
    result = asyncio.run(jwt_auth_dependency(request))
    assert result["user_id"] == "123"


def test_expired_token():
    token = create_token({"user_id": "123"}, expired=True)
    request = make_request_with_token(token)
    with pytest.raises(HTTPException):
        asyncio.run(jwt_auth_dependency(request))
