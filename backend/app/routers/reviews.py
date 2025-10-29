from fastapi import APIRouter, status
from typing import List
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import list_reviews, create_review, delete_review, update_review, get_review_by_id

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("", response_model=List[Review])
def get_reviews():
    return list_reviews()

@router.post("", response_model=Review, status_code=201)
def post_review(payload: ReviewCreate):
    return create_review(payload)

@router.get("/{review_id}", response_model=Review)
def get_review(review_id: str):
    return get_review_by_id(review_id)

@router.put("/{review_id}", response_model=Review)
def put_review(review_id: str, payload: ReviewUpdate):
    return update_review(review_id, payload)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(review_id: str):
    delete_review(review_id)
    return None