from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.user import UserSummaryResponse
from app.middleware.auth_middleware import jwt_auth_dependency
from app.services.user_summary_service import get_user_summary

router = APIRouter(prefix="/home", tags=["home"])

@router.get("/", response_model=UserSummaryResponse, status_code=200)
def get_user_homepage(current_user: dict = Depends(jwt_auth_dependency)):
    user_id = current_user.get("user_id")
    return get_user_summary(user_id)

@router.get("/download", status_code=200)
def download_dashboard(current_user: dict = Depends(jwt_auth_dependency)):
    data = get_user_summary(current_user.get("user_id"))
    headers = {
        "Content-Disposition": "attachment; filename=dashboard.json"
    }
    return JSONResponse(content=data.model_dump(mode="json"), headers=headers)