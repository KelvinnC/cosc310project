from fastapi import APIRouter, status, Depends, HTTPException
from app.schemas.user import UserSummaryResponse
from app.middleware.auth_middleware import jwt_auth_dependency
from app.services.user_summary_service import get_user_summary

router = APIRouter(prefix="/home", tags=["home"])

@router.get("/", response_model=UserSummaryResponse, status_code=200)
def get_user_homepage(current_user: dict = Depends(jwt_auth_dependency)):
    user_id = current_user.get("user_id")
    return get_user_summary(user_id)  