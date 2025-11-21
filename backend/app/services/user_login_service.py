from datetime import datetime, timedelta, timezone
import os

import bcrypt
import jwt
from fastapi import HTTPException

from app.repositories.user_repo import load_all
from app.schemas.user_login import UserLogin

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT SECRET could not be loaded")

INVALID_CREDENTIALS = HTTPException(401, detail="Invalid credentials")


def _build_access_token(found_user: dict) -> str:
    current_datetime = datetime.now(timezone.utc)
    expiration_time = current_datetime + timedelta(hours=1)
    user_payload = {
        "user_id": found_user.get("id"),
        "username": found_user.get("username"),
        "exp": expiration_time,
        "role": found_user.get("role"),
    }
    return jwt.encode(user_payload, JWT_SECRET, algorithm="HS256")


def user_login(payload: UserLogin) -> str:
    users = load_all()
    found_user = next((user for user in users if user.get("username") == getattr(payload, "username", None)), None)
    if found_user is None:
        raise INVALID_CREDENTIALS

    password_valid = bcrypt.checkpw(
        getattr(payload, "password", "").encode("utf-8"),
        found_user.get("hashed_password").encode("utf-8"),
    )
    if not password_valid:
        raise INVALID_CREDENTIALS

    if found_user.get("active") is False:
        raise BannedUserException(403, detail="Account banned")

    return _build_access_token(found_user)


class BannedUserException(HTTPException):
    pass
