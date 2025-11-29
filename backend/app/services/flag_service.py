from datetime import datetime
from app.repositories import flag_repo
from app.services.review_service import get_review_by_id, mark_review_as_flagged, mark_review_as_unflagged
from app.utils.logger import get_logger

logger = get_logger()

def flag_review(user_id: str, review_id: int) -> dict:
    """Flag a review as inappropriate"""
    review = get_review_by_id(review_id)
    
    flags = flag_repo.load_all()
    
    if any(f.get("user_id") == user_id and f.get("review_id") == review_id for f in flags):
        logger.warning(
            "Duplicate flag attempt blocked",
            component="moderation",
            user_id=user_id,
            review_id=review_id
        )
        raise ValueError("User has already flagged this review")
    
    flag_record = {
        "user_id": user_id,
        "review_id": review_id,
        "timestamp": datetime.now().isoformat()
    }
    
    flags.append(flag_record)
    flag_repo.save_all(flags)
    
    mark_review_as_flagged(review)
    
    flag_count = len([f for f in flags if f.get("review_id") == review_id])
    logger.warning(
        "Review flagged by user",
        component="moderation",
        user_id=user_id,
        review_id=review_id,
        total_flags=flag_count
    )
    
    return flag_record

def unflag_review(review_id: int) -> None:
    """Unflag a review"""
    review = get_review_by_id(review_id)

    flags = flag_repo.load_all()

    updated_flags = [f for f in flags if f.get("review_id") != review_id]
    flag_repo.save_all(updated_flags)

    mark_review_as_unflagged(review)

def get_flagged_reviews_count(review_id: int) -> int:
    """Get the number of users who have flagged a specific review"""
    flags = flag_repo.load_all()
    return sum(1 for flag in flags if flag.get("review_id") == review_id)

def has_user_flagged_review(user_id: str, review_id: int) -> bool:
    """Check if a specific user has flagged a specific review"""
    flags = flag_repo.load_all()
    return any(f.get("user_id") == user_id and f.get("review_id") == review_id for f in flags)
