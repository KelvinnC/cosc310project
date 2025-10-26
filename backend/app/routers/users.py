from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import (
    list_users,
    create_user,
    get_user_by_id,
    update_user,
    delete_user
)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[User])
async def get_users():
    return list_users()

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    return get_user_by_id(user_id)

@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "User with this username already exists"},
        422: {"description": "Validation error"}
    }
)
async def create_new_user(user: UserCreate):
    return create_user(user)

@router.put(
    "/{user_id}",
    response_model=User,
    responses={
        404: {"description": "User not found"},
        409: {"description": "Username already taken"},
        422: {"description": "Validation error"}
    }
)
async def update_existing_user(user_id: str, user_update: UserUpdate):
    return update_user(user_id, user_update)

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "User not found"}}
)
async def remove_user(user_id: str):
    delete_user(user_id)
    return None
