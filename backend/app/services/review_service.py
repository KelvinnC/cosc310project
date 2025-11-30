from typing import List, Dict, Any, Optional
from datetime import datetime, date
from math import ceil
from fastapi import HTTPException
from app.schemas.review import Review, ReviewCreate, ReviewUpdate, ReviewWithMovie, PaginatedReviews
from app.repositories.review_repo import load_all, save_all
from app.utils.list_helpers import find_dict_by_id, NOT_FOUND
from app.repositories import movie_repo
from app.services.tmdb_service import is_tmdb_movie_id, validate_tmdb_movie_id, get_tmdb_movie_details, extract_tmdb_id
from app.services.movie_service import cache_tmdb_movie

REVIEW_NOT_FOUND = "Review not found"
DEFAULT_PAGE_SIZE = 20


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

def _filter_by_rating_dicts(
    reviews: List[Dict[str, Any]], rating: Optional[float]
) -> List[Dict[str, Any]]:
    if rating is None:
        return list(reviews)
    target = _to_float(rating)
    return [rv for rv in reviews if _to_float(rv.get("rating")) == target]


async def _build_tmdb_title_cache(reviews: List[Dict[str, Any]]) -> Dict[str, str]:
    """Build a cache of TMDb movie IDs to titles for the given reviews."""
    tmdb_cache: Dict[str, str] = {}
    for rv in reviews:
        movie_id = str(rv.get("movieId", ""))
        if is_tmdb_movie_id(movie_id) and movie_id not in tmdb_cache:
            tmdb_id = extract_tmdb_id(movie_id)
            if tmdb_id:
                try:
                    tmdb_data = await get_tmdb_movie_details(tmdb_id)
                    tmdb_cache[movie_id] = tmdb_data.get("title", "") if tmdb_data else ""
                except Exception:
                    tmdb_cache[movie_id] = ""
    return tmdb_cache


def _get_movie_title(
    raw_movie_id: Any,
    idx_to_uuid: Dict[int, str],
    id_to_title: Dict[str, str],
    tmdb_cache: Dict[str, str],
    default: str = "",
) -> str:
    """Get movie title from local DB or TMDb cache. Single source of truth for title lookup."""
    movie_id_str = str(raw_movie_id) if raw_movie_id else ""
    
    if is_tmdb_movie_id(movie_id_str):
        return tmdb_cache.get(movie_id_str, default)
    
    movie_id = _normalize_movie_id(raw_movie_id, idx_to_uuid)
    return id_to_title.get(movie_id, default) if movie_id else default


def _matches_search_query(
    rv: Dict[str, Any],
    query: str,
    idx_to_uuid: Dict[int, str],
    id_to_title: Dict[str, str],
    tmdb_cache: Dict[str, str],
) -> bool:
    """Check if a review matches a search query (title, body, or movie title)."""
    if query in rv.get("reviewTitle", "").lower():
        return True
    if query in rv.get("reviewBody", "").lower():
        return True
    movie_title = _get_movie_title(rv.get("movieId"), idx_to_uuid, id_to_title, tmdb_cache)
    return query in movie_title.lower()


async def _filter_by_search_async(
    reviews: List[Dict[str, Any]],
    search: Optional[str],
    id_to_title: Dict[str, str],
    idx_to_uuid: Dict[int, str],
) -> List[Dict[str, Any]]:
    """Filter reviews by search query, including TMDb movie titles."""
    if not search:
        return reviews
    
    tmdb_cache = await _build_tmdb_title_cache(reviews)
    query = search.lower()
    return [rv for rv in reviews if _matches_search_query(rv, query, idx_to_uuid, id_to_title, tmdb_cache)]

def _make_rating_sort_key(descending: bool = False):
    def _key(rv: Dict[str, Any]):
        val = _to_float(rv.get("rating"))
        if val is None:
            return (0, 0.0)
        return (1, -val) if descending else (1, val)

    return _key

def _build_movie_indexes() -> tuple[Dict[int, str], Dict[str, str]]:
    movies = movie_repo.load_all()
    idx_to_uuid: Dict[int, str] = {
        idx + 1: mv.get("id")
        for idx, mv in enumerate(movies)
        if isinstance(mv.get("id"), str)
    }
    id_to_title: Dict[str, str] = {
        mv.get("id"): (mv.get("title") or "")
        for mv in movies
        if isinstance(mv.get("id"), str)
    }
    return idx_to_uuid, id_to_title

def _make_movie_id_sort_key(idx_to_uuid: Dict[int, str]):
    def _key(rv: Dict[str, Any]):
        norm = _normalize_movie_id(rv.get("movieId"), idx_to_uuid)
        return (0, "") if norm is None else (1, norm)

    return _key

def _make_movie_title_sort_key(
    idx_to_uuid: Dict[int, str], id_to_title: Dict[str, str]
):
    def _key(rv: Dict[str, Any]):
        mid = _normalize_movie_id(rv.get("movieId"), idx_to_uuid)
        if mid is None:
            return (0, "")
        return (1, id_to_title.get(mid, ""))

    return _key

def _sort_reviews(
    reviews: List[Dict[str, Any]],
    sort_by: Optional[str],
    order: str,
    idx_to_uuid: Dict[int, str],
    id_to_title: Dict[str, str],
) -> List[Dict[str, Any]]:
    """Apply sorting to a list of review dicts."""
    if not sort_by:
        return reviews

    key_name = sort_by.lower()
    descending = order.lower() == "desc"

    if key_name == "rating":
        return sorted(reviews, key=_make_rating_sort_key(descending))

    if key_name in ("movieid", "movietitle"):
        if key_name == "movieid":
            sort_key = _make_movie_id_sort_key(idx_to_uuid)
        else:
            sort_key = _make_movie_title_sort_key(idx_to_uuid, id_to_title)
        return sorted(reviews, key=sort_key, reverse=descending)

    return reviews

def _paginate(
    items: List[Dict[str, Any]], page: int, per_page: int
) -> tuple[List[Dict[str, Any]], int, int]:
    """Return (paginated_items, total, total_pages)."""
    total = len(items)
    total_pages = ceil(total / per_page) if per_page > 0 else 1
    start = (page - 1) * per_page
    return items[start : start + per_page], total, total_pages

async def _enrich_with_movie_titles_async(
    reviews: List[Dict[str, Any]],
    idx_to_uuid: Dict[int, str],
    id_to_title: Dict[str, str],
) -> List[ReviewWithMovie]:
    """Convert review dicts to ReviewWithMovie models with titles (supports TMDb movies)."""
    tmdb_cache = await _build_tmdb_title_cache(reviews)
    result = []
    for review in reviews:
        title = _get_movie_title(review.get("movieId"), idx_to_uuid, id_to_title, tmdb_cache, "Unknown Movie")
        review_data = {**review, "movieId": str(review.get("movieId", ""))}
        result.append(ReviewWithMovie(**review_data, movieTitle=title))
    return result

def filter_and_sort_reviews(
    *,
    rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
) -> List[Review]:
    """Filter and sort reviews, returning Review models."""
    reviews_raw = load_all()
    result = _filter_by_rating_dicts(reviews_raw, rating)
    idx_to_uuid, id_to_title = _build_movie_indexes()
    result = _sort_reviews(result, sort_by, order, idx_to_uuid, id_to_title)
    return [Review(**review) for review in result]

async def list_reviews_paginated(
    *,
    rating: Optional[float] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
    page: int = 1,
    per_page: int = DEFAULT_PAGE_SIZE,
) -> PaginatedReviews:
    """Return paginated reviews with movie titles."""
    reviews_raw = load_all()
    filtered = _filter_by_rating_dicts(reviews_raw, rating)
    idx_to_uuid, id_to_title = _build_movie_indexes()
    # Use async search to include TMDb movie titles
    filtered = await _filter_by_search_async(filtered, search, id_to_title, idx_to_uuid)
    sorted_reviews = _sort_reviews(filtered, sort_by, order, idx_to_uuid, id_to_title)
    paginated, total, total_pages = _paginate(sorted_reviews, page, per_page)
    reviews_with_movies = await _enrich_with_movie_titles_async(paginated, idx_to_uuid, id_to_title)

    return PaginatedReviews(
        reviews=reviews_with_movies,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )

def list_reviews(
    *,
    rating: Optional[float] = None,
    sort_by: Optional[str] = None,
    order: str = "asc",
) -> List[Review]:
    """Return all reviews matching filters (non-paginated)."""
    return filter_and_sort_reviews(rating=rating, sort_by=sort_by, order=order)

def get_leaderboard_reviews(limit: int = 10) -> List[Review]:
    """Return top reviews ranked by votes (descending), limited to `limit`.
    Ties on votes are broken by review date (most recent first).
    """
    reviews = list_reviews()
    sorted_reviews = sorted(
        reviews,
        key=lambda r: (
            getattr(r, "votes", 0),
            getattr(r, "date", None) or date.min,
        ),
        reverse=True,
    )
    return sorted_reviews[:limit]

def get_review_by_id(review_id: int) -> Review:
    """Get a review by ID."""
    reviews = load_all()
    index = find_dict_by_id(reviews, "id", review_id)
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    return Review(**reviews[index])

async def create_review(payload: ReviewCreate, *, author_id: str) -> Review:
    """Create a new review. Validates movie existence (local or TMDb) and assigns author/date.
    
    For TMDb movies: automatically caches the movie to local movies.json so it appears at /movies.
    """
    reviews = load_all(load_invisible=True)
    new_review_id = max((rev.get("id", 0) for rev in reviews), default=0) + 1

    movie_id = payload.movieId.strip()
    
    # Check if it's a TMDb movie or local movie
    if is_tmdb_movie_id(movie_id):
        # Cache TMDb movie locally (this also validates it exists)
        try:
            await cache_tmdb_movie(movie_id)
        except HTTPException:
            raise HTTPException(status_code=400, detail="Invalid movieId: TMDb movie does not exist")
    else:
        # Validate local movie exists
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
    """Update an existing review. Only rating, title, and body can be modified."""
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
        flagged=old_review.get("flagged", False),
        votes=old_review.get("votes", 0),
        date=old_review["date"]
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
    reviews = load_all()
    index = find_dict_by_id(reviews, "id", review.id)
    
    if index == NOT_FOUND:
        raise HTTPException(status_code=404, detail=REVIEW_NOT_FOUND)
    
    reviews[index]["flagged"] = True
    save_all(reviews)

    
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
