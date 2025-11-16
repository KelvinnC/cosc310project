from app.schemas.review import Review
from typing import List
from app.services.review_service import list_reviews, _find_review_index, save_all, NOT_FOUND, REVIEW_NOT_FOUND
from app.repositories.review_repo import load_all
from fastapi import HTTPException
from typing import Dict, Any

def get_flagged_reviews() -> List[Review]:
    reviews = list_reviews()
    return [review for review in reviews if review.flagged]

def hide_review(review_id: int) -> Review:
    """Marks a review's visible field as False"""
    reviews = load_all()
    index = _find_review_index(review_id, reviews)
    
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    
    reviews[index]["visible"] = False
    save_all(reviews)
    return Review(**reviews[index])