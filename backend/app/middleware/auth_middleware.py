from fastapi import Request, HTTPException
import jwt

from app.services.validate_access import validate_user_access


async def jwt_auth_dependency(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Access Token Missing")

    access_token = auth_header.split(" ")[1]

    try:
        payload = validate_user_access(access_token)
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError) as ex:
        # Known JWT validation failure -> 401
        raise HTTPException(status_code=401, detail=str(ex)) from ex
