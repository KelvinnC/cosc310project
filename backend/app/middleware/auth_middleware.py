from fastapi import Request, HTTPException, Depends
from app.services.validate_access import validate_user_access

async def jwt_auth_dependency(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Access Token Missing")
    
    access_token = auth_header.split(" ")[1]

    try:
        payload = validate_user_access(access_token)
        return payload
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))