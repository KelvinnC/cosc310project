from typing import List
from app.schemas.review import Review
from app.repositories.review_repo import load_all as load_reviews
from app.schemas.score import ReviewScore

def get_reviews_by_author(user_id: str) -> List[Review]:
    results: List[ReviewScore] = []
    for rv in load_reviews():
        review_user = rv.get("authorId")
        if review_user == user_id:
            review_score = ReviewScore(rating=rv.get("rating"), reviewTitle = rv.get("reviewTitle"), votes = rv.get("votes"))
            results.append(review_score)
    return results

