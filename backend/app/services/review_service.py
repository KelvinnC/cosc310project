import random
from typing import List
from fastapi import HTTPException
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.repositories.review_repo import load_all, save_all

def list_reviews() -> List[Review]:
    reviews = load_all()
    return [Review(**review) for review in reviews]

def get_review_by_id(review_id: int) -> Review:
    reviews = load_all()
    for review in reviews:
        if review.get("id") == review_id:
            return Review(**review)
    raise HTTPException(status_code=404, detail="Review not found")

def create_review(payload: ReviewCreate) -> Review:
    reviews = load_all()
    new_review_id = max((rev.get("id", 0) for rev in reviews), default=0) + 1
    
    new_review = Review(
        id=new_review_id,
        movieId=payload.movieId.strip(),
        authorId=payload.authorId,
        rating=payload.rating,
        reviewTitle=payload.reviewTitle.strip(),
        reviewBody=payload.reviewBody.strip(),
        date=payload.date
    )
    
    reviews.append(new_review.model_dump(mode="json"))
    save_all(reviews)
    return new_review

def update_review(review_id: int, payload: ReviewUpdate) -> Review:
    reviews = load_all()
    
    for i, review in enumerate(reviews):
        if review.get("id") == review_id:
            updated = Review(
                id=review_id,
                movieId=review["movieId"],
                authorId=review["authorId"],
                rating=payload.rating,
                reviewTitle=payload.reviewTitle.strip(),
                reviewBody=payload.reviewBody.strip(),
                flagged=payload.flagged,
                votes=payload.votes,
                date=payload.date
            )
            reviews[i] = updated.model_dump(mode="json")
            save_all(reviews)
            return updated
    
    raise HTTPException(status_code=404, detail="Review not found")

def delete_review(review_id: int):
    reviews = load_all()
 
    updated_reviews = [r for r in reviews if r.get("id") != review_id]
    
    if len(updated_reviews) == len(reviews):
        raise HTTPException(status_code=404, detail="Review not found")
    
    save_all(updated_reviews)

def sample_reviews_for_battle(user_id: str, sample_size: int = 200) -> List[Review]:
    reviews = load_all()

    filtered_reviews = [Review(**review) for review in reviews if review["authorId"] != user_id]

    if len(filtered_reviews) > sample_size:
        return random.sample(filtered_reviews, sample_size)
    
    return filtered_reviews