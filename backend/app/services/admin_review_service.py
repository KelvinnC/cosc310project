from app.schemas.review import Review
from typing import List
from app.services.review_service import list_reviews

def get_flagged_reviews() -> List[Review]:
    reviews = list_reviews()
    return [review for review in reviews if review.flagged]