from fastapi import Depends, HTTPException
from app.middleware.auth_middleware import jwt_auth_dependency

def admin_required(current_user: dict = Depends(jwt_auth_dependency)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, detail="Unauthorized action")
    return current_user