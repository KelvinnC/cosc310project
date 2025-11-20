from fastapi import APIRouter, Depends, HTTPException, status
from app.services.admin_summary_service import get_admin_summary_data
from app.middleware.admin_dependency import admin_required
from app.schemas.admin import AdminSummaryResponse

from typing import Dict, Any

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/", response_model=AdminSummaryResponse, status_code=status.HTTP_200_OK)
def get_admin_summary(current_user: dict = Depends(admin_required)):
    return get_admin_summary_data()