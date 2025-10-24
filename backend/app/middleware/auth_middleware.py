from fastapi import Request, HTTPException
from app.services.validate_access import validate_user_access

async def jwt_auth_middleware(request: Request, call_next):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code = 401, detail = "Access Token Missing")
    
    access_token = auth_header.split(" ")[1]

    try:
        payload = validate_user_access(access_token)
        request.state.user = payload
    except Exception as ex:
        raise HTTPException(status_code=401, detail=str(ex))
    response = await call_next(request)
    return response