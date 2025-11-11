from fastapi import APIRouter, status, Depends, HTTPException
from app.services.admin_service import get_banned_users, get_user_count, get_warned_users
from app.middleware.auth_middleware import jwt_auth_dependency

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/")
def get_admin_summary(current_user: dict = Depends(jwt_auth_dependency)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, detail="Unauthorized action")
    admin_summary = {
        "total_users": get_user_count(),
        "warned_users": get_warned_users(),
        "banned_users": get_banned_users()
    }
    return admin_summary