import uuid
from typing import List, Dict, Any
from fastapi import HTTPException
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.repositories.movie_repo import load_all, save_all

def list_reviews() -> List[Review]:
    return [Review(**rw) for rw in load_all()]

def create_review(payload: ReviewCreate) -> Review:
    reviews = load_all()
    new_review_id = str(uuid.uuid4())
    if any(rev.get("id") == new_review_id for rev in reviews):
        raise HTTPException(status_code=409, detail="ID collision; retry")
    new_review = Review(id=new_review_id, movieId=payload.movieId, authorId=payload.authorId, rating=payload.rating, reviewTitle=payload.reviewTitle.strip(), 
                        reviewBody=payload.reviewBody.strip(), date=payload.date)
    reviews.append(new_review.model_dump(mode="json")) #model_dump auto serializes fields like dates
    save_all(reviews)
    return new_review

def get_review_by_id(review_id: str) -> Review:
    reviews = load_all()
    for review in reviews:
        if str(review.get("id")) == review_id:
            return Review(**review)
    raise HTTPException(status_code=404, detail=f"Movie '{review_id}' not found")

def update_review(review_id: str, payload: ReviewUpdate) -> Review:
    reviews = load_all()
    for idx, review in enumerate(reviews):
        if review.get("id") == review_id:
            updated = Review(id=review_id, movieId=payload.movieId, authorId=payload.authorId, rating=payload.rating, reviewTitle=payload.reviewTitle.strip(), 
                        reviewBody=payload.reviewBody.strip(), date=payload.date)
            reviews[idx] = updated.model_dump(mode="json")
            save_all(reviews)
            return updated
    raise HTTPException(status_code=404, detail=f"Movie '{review_id}' not found")

def delete_review(review_id: str) -> None:
    reviews = load_all()
    new_reviews = [review for review in reviews if review.get("id") != review_id]
    if len(new_reviews) == len(reviews):
        raise HTTPException(status_code=404, detail=f"Movie '{review_id}' not found")
    save_all(new_reviews)