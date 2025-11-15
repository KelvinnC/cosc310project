from typing import List
from app.schemas.review import Review
from app.repositories.review_repo import load_all as load_reviews
from app.schemas.score import ReviewScore

def get_reviews_by_author(user_id: str) -> List[ReviewScore]:
    results = []
    for rv in load_reviews():
        if rv.get("authorId") == user_id:
            review_score = ReviewScore(
                rating=rv.get("rating"),
                reviewTitle=rv.get("reviewTitle"),
                votes=str(rv.get("votes"))
            )
            results.append(review_score)
    return results
