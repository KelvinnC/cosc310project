import jwt
import os

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("JWT SECRET could not be loaded")

def validate_user_access(access_token):
    try:
        jwt_decoded = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        return jwt_decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

