from fastapi import APIRouter, Depends, HTTPException, status
from app.services.admin_user_service import get_banned_users, get_user_count, get_warned_users
from app.services.admin_review_service import get_flagged_reviews
from app.middleware.admin_dependency import admin_required

from typing import Dict, Any

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def get_admin_summary(current_user: dict = Depends(admin_required)):
    admin_summary = {
        "total_users": get_user_count(),
        "warned_users": get_warned_users(),
        "banned_users": get_banned_users(),
        "flagged_reviews": get_flagged_reviews()
    }
    return admin_summary