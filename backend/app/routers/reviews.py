from fastapi import APIRouter, status, Query, HTTPException, Depends
from typing import List

from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.schemas.search import MovieSearch, MovieWithReviews
from app.services.review_service import list_reviews, create_review, delete_review, update_review, get_review_by_id
from app.services.search_service import search_movies_with_reviews
from app.services import flag_service
from app.middleware.auth_middleware import jwt_auth_dependency

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.get("", response_model=List[Review])
def get_reviews():
    """Retrieve all reviews."""
    return list_reviews()

@router.post("", response_model=Review, status_code=201)
def post_review(review: ReviewCreate):
    """Create a new review."""
    return create_review(review)

@router.get("/search", response_model=List[MovieWithReviews])
def search_reviews(title: str = Query(..., min_length=1)):
    """Search for movies with reviews by title."""
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)

@router.get("/{review_id}", response_model=Review)
def get_review(review_id: int):
    """Retrieve a review by ID."""
    try:
        return get_review_by_id(review_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )

@router.put("/{review_id}", response_model=Review)
def put_review(review_id: int, review_update: ReviewUpdate):
    """Update a review by ID."""
    try:
        return update_review(review_id, review_update)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(review_id: int):
    """Delete a review by its ID. Returns 204 on success, 404 if not found."""
    try:
        delete_review(review_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )
    return None


@router.post("/{review_id}/flag", status_code=status.HTTP_201_CREATED)
def flag_review(review_id: int, current_user: dict = Depends(jwt_auth_dependency)):
    """Flag a review as inappropriate."""
    user_id = current_user.get("user_id")
    
    try:
        flag_record = flag_service.flag_review(user_id, review_id)
        return {
            "message": "Review flagged successfully",
            "review_id": review_id,
            "flagged_at": flag_record["timestamp"]
        }
    except ValueError as e:
        error_msg = str(e)
        if "already flagged" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to flag review: {str(e)}"
        )