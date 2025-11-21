from typing import List
from datetime import datetime
from fastapi import HTTPException
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.repositories.review_repo import load_all, save_all
from app.utils.list_helpers import find_dict_by_id, NOT_FOUND
from app.repositories import movie_repo

REVIEW_NOT_FOUND = "Review not found"

def list_reviews() -> List[Review]:
    """List all reviews."""
    reviews = load_all()
    return [Review(**review) for review in reviews]

def get_review_by_id(review_id: int) -> Review:
    """Get a review by ID."""
    reviews = load_all()
    index = find_dict_by_id(reviews, "id", review_id)
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    return Review(**reviews[index])

def create_review(payload: ReviewCreate, *, author_id: str) -> Review:
    """Create a new review. Validates movie existence and assigns author/date."""
    reviews = load_all(load_invisible=True)
    new_review_id = max((rev.get("id", 0) for rev in reviews), default=0) + 1

    movie_id = payload.movieId.strip()
    movies = movie_repo.load_all()
    if not any(m.get("id") == movie_id for m in movies):
        raise HTTPException(status_code=400, detail="Invalid movieId: movie does not exist")
    
    new_review = Review(
        id=new_review_id,
        movieId=movie_id,
        authorId=author_id,
        rating=payload.rating,
        reviewTitle=payload.reviewTitle,
        reviewBody=payload.reviewBody,
        date=datetime.now().date()
    )

    reviews.append(new_review.model_dump(mode="json"))
    save_all(reviews)
    return new_review

def update_review(review_id: int, payload: ReviewUpdate) -> Review:
    """Update an existing review."""
    reviews = load_all(load_invisible=True)
    index = find_dict_by_id(reviews, "id", review_id)

    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    
    old_review = reviews[index]
    updated_review = Review(
        id=review_id,
        movieId=old_review["movieId"],
        authorId=old_review["authorId"],
        rating=payload.rating,
        reviewTitle=payload.reviewTitle,
        reviewBody=payload.reviewBody,
        flagged=payload.flagged,
        votes=payload.votes,
        date=payload.date
    )

    reviews[index] = updated_review.model_dump(mode="json")
    save_all(reviews)
    return updated_review

def delete_review(review_id: int):
    """Delete a review by ID."""
    reviews = load_all(load_invisible=True)
    index = find_dict_by_id(reviews, "id", review_id)
    
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    
    reviews.pop(index)
    save_all(reviews)

def increment_vote(review_id: int) -> None:
    """Increment the vote count for a review."""
    reviews = load_all(load_invisible=True)
    index = find_dict_by_id(reviews, "id", review_id)
    
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    
    reviews[index]["votes"] = reviews[index].get("votes", 0) + 1
    save_all(reviews)

def mark_review_as_flagged(review: Review) -> None:
    """Mark a review as flagged"""
    review_update = ReviewUpdate(
        rating=review.rating,
        reviewTitle=review.reviewTitle,
        reviewBody=review.reviewBody,
        flagged=True,
        votes=review.votes,
        date=review.date
    )
    update_review(review.id, review_update)

def mark_review_as_unflagged(review: Review) -> None:
    """Mark a review as unflagged"""
    reviews = load_all(load_invisible=True)
    index = find_dict_by_id(reviews, "id", review.id)

    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)

    reviews[index]["flagged"] = False
    save_all(reviews)
    
def get_reviews_by_author(user_id: str) -> List[Review]:
    results = []
    for rv in load_all():
        if rv.get("authorId") == user_id:
            results.append(Review(**rv))
    return results
