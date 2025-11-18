from app.services.review_service import get_reviews_by_author
from app.schemas.review import Review
from typing import List
from app.services.battle_pair_selector import load_user_battles
from app.services.user_service import get_user_by_id
from app.schemas.user import User

def get_users_reviews(current_user_id: str) -> List[Review]:
    """Gets the current user's reviews"""
    return get_reviews_by_author(current_user_id)

def get_users_battles(current_user_id: str) -> List[dict]:
    """Gets the current user's battles"""
    return load_user_battles(current_user_id)

def get_user_object(current_user_id: str) -> User:
    """Gets the current user's user object"""
    return get_user_by_id(current_user_id)