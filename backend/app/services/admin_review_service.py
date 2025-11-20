from app.schemas.review import Review
from typing import List
from app.services.review_service import list_reviews, save_all, NOT_FOUND, REVIEW_NOT_FOUND
from app.utils.list_helpers import find_dict_by_id
from app.repositories.review_repo import load_all
from fastapi import HTTPException
from typing import Dict, Any
from app.utils.logger import get_logger

def get_flagged_reviews() -> List[Review]:
    reviews = list_reviews()
    return [review for review in reviews if review.flagged]

def hide_review(review_id: int) -> Review:
    """Marks a review's visible field as False"""
    logger = get_logger()
    reviews = load_all(load_invisible=True)
    index = find_dict_by_id(reviews, "id", review_id)
    
    if index == NOT_FOUND:
        logger.warning(
            "Admin attempted to hide non-existent review",
            component="admin",
            review_id=review_id
        )
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    
    reviews[index]["visible"] = False
    save_all(reviews)
    logger.warning(
        "Review hidden by admin",
        component="admin",
        review_id=review_id,
        author_id=reviews[index].get("author_id")
    )
    return Review(**reviews[index])