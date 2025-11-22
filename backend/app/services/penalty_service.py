from app.repositories.user_repo import load_all, save_all
from fastapi import HTTPException
from app.services.user_service import get_user_by_id
from app.schemas.user import User
from app.utils.logger import get_logger

logger = get_logger()

def _save_updated_user(user, user_id):
    """Replace the old user with the updated one and save all users"""
    users = [usr for usr in load_all() if usr.get("id") != user_id]
    users.append(user.model_dump(mode="json"))
    save_all(users)

def warn_user(user_id: str) -> User:
    user = get_user_by_id(user_id, show_password=True)
    user.warnings += 1
    _save_updated_user(user, user_id)
    logger.warning(
        "User warned by admin",
        component="admin",
        user_id=user_id,
        new_warning_count=user.warnings
    )
    return user

def unwarn_user(user_id: str) -> User:
    user = get_user_by_id(user_id, show_password=True)
    old_warning_count = user.warnings
    user.warnings = max(0, user.warnings - 1)
    _save_updated_user(user, user_id)
    logger.info(
        "User warning removed by admin",
        component="admin",
        user_id=user_id,
        old_warning_count=old_warning_count,
        new_warning_count=user.warnings
    )
    return user

def ban_user(user_id: str) -> User:
    user = get_user_by_id(user_id, show_password=True)
    user.active = False
    _save_updated_user(user, user_id)
    logger.error(
        "User banned by admin",
        component="admin",
        user_id=user_id
    )
    return user

def unban_user(user_id: str) -> User:
    user = get_user_by_id(user_id, show_password=True)
    user.active = True
    _save_updated_user(user, user_id)
    logger.info(
        "User unbanned by admin",
        component="admin",
        user_id=user_id
    )
    return user