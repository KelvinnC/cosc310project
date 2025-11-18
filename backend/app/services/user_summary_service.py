from app.services.review_service import get_reviews_by_author
from app.schemas.review import Review
from typing import List

def get_users_reviews(current_user_id: str) -> List[Review]:
    """Gets the current user's reviews"""
    return get_reviews_by_author(current_user_id)