from datetime import datetime
from app.repositories import flag_repo
from app.services.review_service import get_review_by_id, update_review
from app.schemas.review import ReviewUpdate


def has_user_flagged_review(user_id: str, review_id: int) -> bool:
    flags = flag_repo.load_all()
    for flag in flags:
        if flag.get("user_id") == user_id and flag.get("review_id") == review_id:
            return True
    return False

def flag_review(user_id: str, review_id: int) -> dict:
    """Flag a review as inappropriate"""
    if has_user_flagged_review(user_id, review_id):
        raise ValueError("User has already flagged this review")
    
    review = get_review_by_id(review_id)
    
    flag_record = {
        "user_id": user_id,
        "review_id": review_id,
        "timestamp": datetime.now().isoformat()
    }
    
    flags = flag_repo.load_all()
    flags.append(flag_record)
    flag_repo.save_all(flags)
    
    review_update = ReviewUpdate(
        rating=review.rating,
        reviewTitle=review.reviewTitle,
        reviewBody=review.reviewBody,
        flagged=True,
        votes=review.votes,
        date=review.date
    )
    update_review(review_id, review_update)
    
    return flag_record

def get_flagged_reviews_count(review_id: int) -> int:
    """Get the number of users who have flagged a specific review"""
    flags = flag_repo.load_all()
    return sum(1 for flag in flags if flag.get("review_id") == review_id)

def get_all_flagged_reviews() -> list:
    """Get all reviews that have been flagged"""
    from app.services.review_service import list_reviews
    all_reviews = list_reviews()
    return [r for r in all_reviews if r.flagged]
