import random
from typing import List, Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from app.schemas.review import Review, ReviewCreate, ReviewUpdate
from app.repositories.review_repo import load_all, save_all
from app.utils.list_helpers import find_dict_by_id, NOT_FOUND
from app.repositories import movie_repo

REVIEW_NOT_FOUND = "Review not found"


def _to_float(val: Any) -> Optional[float]:
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _normalize_movie_id(raw_id: Any, idx_to_uuid: Dict[int, str]) -> Optional[str]:
    if isinstance(raw_id, str):
        return raw_id
    if isinstance(raw_id, int):
        return idx_to_uuid.get(raw_id)
    return None


def list_reviews(
    *,
    rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
) -> List[Review]:
    """Filtering:
        - If `rating` is provided, include only reviews whose numeric rating
          equals this value. Non-numeric ratings won't match.
    Sorting:
        - `sort_by` supports 'rating', 'movieId', or 'movieTitle'
          with `order` controlling ascending or descending.
    """
    reviews_raw = load_all()
    result: List[Dict[str, Any]] = list(reviews_raw)

    if rating is not None:
        target = _to_float(rating)
        result = [rv for rv in result if _to_float(rv.get("rating")) == target]

    if sort_by:
        key = (sort_by or "").lower()
        reverse = (order or "asc").lower() == "desc"

        if key == "rating":
            def _rating_key(rv: Dict[str, Any]):
                val = _to_float(rv.get("rating"))
                if val is None:
                    return (0, 0.0)
                return (1, val)
            # Always sort ascending by the tuple key; we want "invalid"
            # ratings to come first, and reverse order for val handled
            # by negating in the key when order is descending.
            if reverse:
                def _rating_key(rv: Dict[str, Any]):
                    val = _to_float(rv.get("rating"))
                    if val is None:
                        return (0, 0.0)
                    return (1, -val)

            result = sorted(result, key=_rating_key)

        elif key in ("movieid", "movietitle"):
            movies = movie_repo.load_all()
            idx_to_uuid: Dict[int, str] = {
                idx + 1: mv.get("id") for idx, mv in enumerate(movies) if isinstance(mv.get("id"), str)
            }

            if key == "movieid":
                def _movie_id_key(rv: Dict[str, Any]):
                    norm = _normalize_movie_id(rv.get("movieId"), idx_to_uuid)
                    return (0, "") if norm is None else (1, norm)

                result = sorted(result, key=_movie_id_key, reverse=reverse)
            else:
                id_to_title: Dict[str, str] = {}
                for mv in movies:
                    mid = mv.get("id")
                    title = mv.get("title") or ""
                    if isinstance(mid, str):
                        id_to_title[mid] = title

                def _movie_title_key(rv: Dict[str, Any]):
                    mid = _normalize_movie_id(rv.get("movieId"), idx_to_uuid)
                    if mid is None:
                        return (0, "")
                    return (1, id_to_title.get(mid, ""))

                result = sorted(result, key=_movie_title_key, reverse=reverse)

    return [Review(**review) for review in result]

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


def get_reviews_by_author(user_id: str) -> List[Review]:
    results = []
    for rv in load_all():
        if rv.get("authorId") == user_id:
            results.append(Review(**rv))
    return results
