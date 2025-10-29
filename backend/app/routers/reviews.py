from fastapi import APIRouter, status
from typing import List
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import list_reviews, create_review, delete_review, update_review, get_review_by_id

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[Review])
def get_reviews():
    return list_reviews()

@router.post("", response_model=Review, status_code=201)
def post_movie(payload: ReviewCreate):
    return create_review(payload)

@router.get("/{movie_id}", response_model=Review)
def get_movie(movie_id: str):
    return get_review_by_id(movie_id)

@router.put("/{movie_id}", response_model=Review)
def put_movie(movie_id: str, payload: ReviewUpdate):
    return update_review(movie_id, payload)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie(movie_id: str):
    delete_review(movie_id)
    return None