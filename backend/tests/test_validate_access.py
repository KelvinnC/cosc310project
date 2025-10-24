import pytest
import jwt
import os
from datetime import datetime, timedelta, timezone

from app.services.validate_access import validate_user_access

JWT_SECRET = os.getenv("JWT_SECRET")


def create_token(payload: dict, expired: bool = False):
    exp = datetime.now(timezone.utc) - timedelta(seconds=10) if expired else datetime.now(timezone.utc) + timedelta(minutes=5)
    token = jwt.encode({**payload, "exp": exp}, JWT_SECRET, algorithm="HS256")
    return token


def test_valid_token():
    token = create_token({"username": "testuser", "role": "user"})
    decoded = validate_user_access(token)
    assert isinstance(decoded, dict)
    assert decoded["username"] == "testuser"
    assert decoded["role"] == "user"


def test_expired_token():
    token = create_token({"username": "expired_user"}, expired=True)
    result = validate_user_access(token)
    assert result == jwt.ExpiredSignatureError


def test_invalid_token():
    invalid_token = "this.is.not.a.valid.token"
    result = validate_user_access(invalid_token)
    assert result == jwt.InvalidTokenError


def test_tampered_token():
    token = create_token({"username": "user123"})
    tampered = token[:-2] + "xx"
    result = validate_user_access(tampered)
    assert result == jwt.InvalidTokenError
