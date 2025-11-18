from app.services.review_service import get_reviews_by_author
from app.schemas.review import Review
from typing import List
from app.services.battle_pair_selector import load_user_battles

def get_users_reviews(current_user_id: str) -> List[Review]:
    """Gets the current user's reviews"""
    return get_reviews_by_author(current_user_id)

def get_users_battles(current_user_id: str) -> List[dict]:
    """Gets the current user's battles"""
    return load_user_battles(current_user_id)