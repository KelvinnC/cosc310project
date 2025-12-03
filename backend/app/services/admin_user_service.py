from app.repositories.user_repo import load_all
from app.schemas.user import User
from app.services.user_service import list_users
from typing import List


def get_user_count() -> int:
    users = load_all()
    return len(users)


def get_warned_users() -> List[User]:
    users = list_users()
    warned_users = [user for user in users if user.warnings > 0]
    return warned_users


def get_banned_users() -> List[User]:
    users = list_users()
    banned_users = [user for user in users if not user.active]
    return banned_users
