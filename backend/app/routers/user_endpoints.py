from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import list_users, get_user_by_id, update_user, create_user, delete_user
from app.services.penalty_service import warn_user, unwarn_user, ban_user, unban_user
from app.middleware.auth_middleware import jwt_auth_dependency

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/", response_model=List[User])
def get_users():
    return list_users()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    return get_user_by_id(user_id)

@router.post("/", response_model=User, status_code=201)
def add_user(payload: UserCreate):
    return create_user(payload)

@router.put("/{user_id}", response_model=User)
def put_user(user_id: str, payload: UserUpdate):
    return update_user(user_id, payload)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id: str):
    delete_user(user_id)
    return None

@router.patch("/{user_id}/warn", response_model=User)
def add_user_warning(user_id: str, current_user: dict = Depends(jwt_auth_dependency)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, detail="Unauthorized action")
    return warn_user(user_id)

@router.patch("/{user_id}/unwarn", response_model=User)
def remove_user_warning(user_id: str, current_user: dict = Depends(jwt_auth_dependency)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, detail="Unauthorized action")
    return unwarn_user(user_id)

@router.patch("/{user_id}/ban", response_model=User)
def add_user_ban(user_id: str, current_user: dict = Depends(jwt_auth_dependency)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, detail="Unauthorized action")
    return ban_user(user_id)

@router.patch("/{user_id}/unban", response_model=User)
def remove_user_ban(user_id: str, current_user: dict = Depends(jwt_auth_dependency)):
    if current_user.get("role") != "admin":
        raise HTTPException(403, detail="Unauthorized action")
    return unban_user(user_id)