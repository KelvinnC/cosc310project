from fastapi import APIRouter, status
from app.schemas.user_login import UserLogin
from app.services.user_login_service import user_login

router = APIRouter(prefix="/login", tags=["login"])

@router.post("", status_code=201)
def login(payload: UserLogin):
    return user_login(payload)