from fastapi import APIRouter, status
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import list_users, get_user_by_id, update_user, create_user, delete_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[User])
def get_users():
    return list_users()

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    return get_user_by_id(user_id)

@router.post("", response_model=User)
def add_user(payload: UserCreate):
    return create_user(payload)

@router.put("{user_id}", response_model=User)
def put_user(user_id: str, payload: UserUpdate):
    return update_user(user_id, payload)

@router.delete("{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id: str):
    delete_user(user_id)
    return None