from fastapi import APIRouter, status, Depends, HTTPException
from typing import List
from app.schemas.user import User, UserCreate, UserUpdate
from app.services.user_service import list_users, get_user_by_id, update_user, create_user, delete_user
from app.services.penalty_service import warn_user, unwarn_user, ban_user, unban_user
from app.middleware.admin_dependency import admin_required

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User], summary="List all users")
def get_users():
    """Retrieve all registered users in the system."""
    return list_users()


@router.get("/{user_id}", response_model=User, summary="Get user by ID")
def get_user(user_id: str):
    """Retrieve a specific user by their unique ID."""
    return get_user_by_id(user_id)


@router.post("/", response_model=User, status_code=201, summary="Register new user")
def add_user(payload: UserCreate):
    """
    Create a new user account.

    - **username**: Unique username for the account
    - **password**: Account password (will be hashed)
    - **role**: User role (user/admin)
    """
    return create_user(payload)


@router.put("/{user_id}", response_model=User, summary="Update user")
def put_user(user_id: str, payload: UserUpdate):
    """Update an existing user's information."""
    return update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user")
def remove_user(user_id: str):
    """Permanently delete a user account and all associated data."""
    delete_user(user_id)
    return None


@router.patch("/{user_id}/warn", response_model=User, summary="Warn user (Admin)")
def add_user_warning(user_id: str, current_user: dict = Depends(admin_required)):
    """Issue a warning to a user. Requires admin privileges."""
    return warn_user(user_id)


@router.patch("/{user_id}/unwarn", response_model=User, summary="Remove warning (Admin)")
def remove_user_warning(user_id: str, current_user: dict = Depends(admin_required)):
    """Remove a warning from a user. Requires admin privileges."""
    return unwarn_user(user_id)


@router.patch("/{user_id}/ban", response_model=User, summary="Ban user (Admin)")
def add_user_ban(user_id: str, current_user: dict = Depends(admin_required)):
    """Ban a user from the platform. Requires admin privileges."""
    return ban_user(user_id)


@router.patch("/{user_id}/unban", response_model=User, summary="Unban user (Admin)")
def remove_user_ban(user_id: str, current_user: dict = Depends(admin_required)):
    """Lift a ban from a user. Requires admin privileges."""
    return unban_user(user_id)
