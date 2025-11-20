import os
from typing import Dict, Any

import jwt

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT SECRET could not be loaded")


def validate_user_access(access_token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT access token.
    Returns the decoded payload on success or lets jwt decode errors propagate.
    """
    return jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])

