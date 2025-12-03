from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.user import UserSummaryResponse
from app.middleware.auth_middleware import jwt_auth_dependency
from app.services.user_summary_service import get_user_summary

router = APIRouter(prefix="/home", tags=["home"])


@router.get("/", response_model=UserSummaryResponse, status_code=200, summary="Get user dashboard")
def get_user_homepage(current_user: dict = Depends(jwt_auth_dependency)):
    """
    Retrieve the authenticated user's personalized dashboard.

    Includes user profile, recent reviews, battle statistics, and activity summary.
    """
    user_id = current_user.get("user_id")
    return get_user_summary(user_id)


@router.get("/download", status_code=200, summary="Download activity history")
def download_dashboard(current_user: dict = Depends(jwt_auth_dependency)):
    """
    Download the user's dashboard data as a JSON file.

    Returns a downloadable file containing the user's complete activity history.
    """
    data = get_user_summary(current_user.get("user_id"))
    headers = {
        "Content-Disposition": "attachment; filename=dashboard.json"
    }
    return JSONResponse(content=data.model_dump(mode="json"), headers=headers)
