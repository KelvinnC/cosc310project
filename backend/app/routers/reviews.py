from fastapi import APIRouter, status
from typing import List
from fastapi import APIRouter, Query
from app.schemas.search import MovieSearch, MovieWithReviews
from app.services.search_service import search_movies_with_reviews

from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.services.review_service import list_reviews, create_review, delete_review, update_review, get_review_by_id

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("", response_model=List[Review])
def get_reviews():
    """Retrieve all reviews."""
    return list_reviews()

@router.get("/search", response_model=List[MovieWithReviews])
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)

@router.post("", response_model=Review, status_code=201)
def post_review(review: ReviewCreate):
    """Create a new review."""
    return create_review(review)

@router.get("/search/", include_in_schema=False, response_model=List[MovieWithReviews])
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)
@router.get("/{review_id}", response_model=Review)
def get_review(review_id: int):
    """Retrieve a review by ID."""
    return get_review_by_id(review_id)

@router.put("/{review_id}", response_model=Review)
def put_review(review_id: int, review_update: ReviewUpdate):
    """Update a review by ID."""
    return update_review(review_id, review_update)

@router.get("", include_in_schema=False, response_model=List[MovieWithReviews])
def search_reviews_on_collection(title: str = Query(None)):
    if not title:
        return []
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(review_id: int):
    """Delete a review by its ID."""
    delete_review(review_id)
    return None