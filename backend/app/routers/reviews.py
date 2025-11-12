from typing import List, Optional, Literal
from fastapi import APIRouter, Query
from app.schemas.search import MovieSearch, MovieWithReviews
from app.schemas.review import Review
from app.services.search_service import search_movies_with_reviews
from app.repositories.review_repo import get_all_reviews


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/search", response_model=List[MovieWithReviews])
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)


@router.get("/search/", include_in_schema=False, response_model=List[MovieWithReviews])
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)


@router.get("", response_model=List[Review])
def list_or_filter_reviews(
    rating: Optional[float] = Query(None, ge=1, le=5),
    sort_by: Optional[Literal["rating", "movie"]] = Query(None),
    order: Literal["asc", "desc"] = Query("asc"),
):
    repo_sort = None
    if sort_by == "rating":
        repo_sort = "rating"
    elif sort_by == "movie":
        repo_sort = "movieTitle"
    return get_all_reviews(rating=rating, sort_by=repo_sort, order=order)


@router.get("/filter", include_in_schema=False)
def filter_reviews(
    rating: Optional[float] = Query(None, ge=1, le=5),
    sort_by: Optional[Literal["rating", "movie"]] = Query(None),
    order: Literal["asc", "desc"] = Query("asc"),
):
    return list_or_filter_reviews(rating=rating, sort_by=sort_by, order=order)
