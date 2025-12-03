from fastapi import APIRouter, status
from app.schemas.user_login import UserLogin
from app.services.user_login_service import user_login

router = APIRouter(prefix="/login", tags=["login"])


@router.post("", status_code=201, summary="Authenticate user")
def login(payload: UserLogin):
    """
    Authenticate a user and return a JWT access token.
    
    - **username**: User's registered username
    - **password**: User's password
    
    Returns a bearer token for authenticated API requests.
    """
    token = user_login(payload)
    return {"access_token": token, "token_type": "bearer"}