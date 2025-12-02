from typing import List, Optional, Literal
from fastapi import APIRouter, status, Query, HTTPException, Depends
from app.schemas.review import Review, ReviewCreate, ReviewUpdate, PaginatedReviews
from app.schemas.comment import CommentWithAuthor, CommentCreate
from app.schemas.search import MovieSearch, MovieWithReviews
from app.services.review_service import (
    list_reviews_paginated,
    create_review,
    delete_review,
    update_review,
    get_review_by_id,
    get_reviews_by_author,
)
from app.services.search_service import search_movies_with_reviews
from app.services import flag_service
from app.services.comment_service import get_comments_by_review_id, create_comment
from app.middleware.auth_middleware import jwt_auth_dependency, jwt_auth_optional
from app.middleware.admin_dependency import admin_required
from app.services.admin_review_service import hide_review

router = APIRouter(prefix="/reviews", tags=["reviews"])

@router.post("", response_model=Review, status_code=201)
async def post_review(review: ReviewCreate, current_user: dict = Depends(jwt_auth_dependency)):
    """Create a new review."""
    author_id = current_user.get("user_id")
    return await create_review(review, author_id=author_id)

@router.get("/search", response_model=List[MovieWithReviews])
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)


@router.get("/search/", include_in_schema=False, response_model=List[MovieWithReviews])
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)


@router.get("", response_model=PaginatedReviews)
def list_or_filter_reviews(
    rating: Optional[float] = Query(None, ge=1, le=5),
    search: Optional[str] = Query(None, min_length=1),
    sort_by: Optional[Literal["rating", "movie"]] = Query(None),
    order: Literal["asc", "desc"] = Query("asc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
):
    service_sort = None
    if sort_by == "rating":
        service_sort = "rating"
    elif sort_by == "movie":
        service_sort = "movieTitle"

    return list_reviews_paginated(
        rating=rating,
        search=search,
        sort_by=service_sort,
        order=order,
        page=page,
        per_page=per_page
    )


@router.get("/filter", include_in_schema=False)
def filter_reviews(
    rating: Optional[float] = Query(None, ge=1, le=5),
    search: Optional[str] = Query(None, min_length=1),
    sort_by: Optional[Literal["rating", "movie"]] = Query(None),
    order: Literal["asc", "desc"] = Query("asc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=500),
):
    return list_or_filter_reviews(rating=rating, search=search, sort_by=sort_by, order=order, page=page, per_page=per_page)

@router.get("/{review_id}", response_model=Review)
def get_review(review_id: int):
    """Retrieve a review by ID."""
    try:
        return get_review_by_id(review_id)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )

@router.get("/author/{author_id}", response_model=List[Review])
def get_author_reviews(author_id: str):
    try:
        return get_reviews_by_author(author_id)
    except HTTPException as exc:
        if getattr(exc, "status_code", None) == 404:
            return []
        raise

@router.put("/{review_id}", response_model=Review)
def put_review(review_id: int, review_update: ReviewUpdate, current_user: dict | None = Depends(jwt_auth_optional)):
    """Update a review by ID."""
    try:
        if current_user:
            existing = get_review_by_id(review_id)
            if str(existing.authorId) != str(current_user.get("user_id")):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only modify your own reviews"
                )

        return update_review(review_id, review_update)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review {review_id} not found"
        )

@router.patch("/{review_id}/hide", response_model=Review)
def hide_inappropriate_review(review_id: int, current_user=Depends(admin_required)):
    return hide_review(review_id)

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_review(review_id: int, current_user: dict | None = Depends(jwt_auth_optional)):
    """Delete a review by its ID. Returns 204 on success, 404 if not found."""
    try:
        if current_user:
            existing = get_review_by_id(review_id)
            if str(existing.authorId) != str(current_user.get("user_id")):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only modify your own reviews"
                )

        delete_review(review_id)
    except HTTPException:
        raise
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

@router.get("/{review_id}/flag/status")
def get_flag_status(review_id: int, current_user: dict = Depends(jwt_auth_dependency)):
    """Check if the current user has flagged this review."""
    user_id = current_user.get("user_id")
    has_flagged = flag_service.has_user_flagged_review(user_id, review_id)
    return {"has_flagged": has_flagged}

@router.post("/{review_id}/unflag", status_code=204)
def flag_review(review_id: int, current_user: dict = Depends(admin_required)):
    """Unflag a review. Admin only endpoint"""
    flag_service.unflag_review(review_id)


@router.get("/{review_id}/comments", response_model=List[CommentWithAuthor])
def list_comments(review_id: int):
    """List comments for a review."""
    return get_comments_by_review_id(review_id)


@router.post("/{review_id}/comments", status_code=status.HTTP_204_NO_CONTENT)
def post_comment(
    review_id: int,
    payload: CommentCreate,
    current_user: dict = Depends(jwt_auth_dependency),
):
    """Create a new comment on a review."""
    create_comment(payload, review_id=review_id, user_id=current_user.get("user_id"))
    return None
