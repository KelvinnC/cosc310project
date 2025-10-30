from typing import List
from fastapi import APIRouter, Query
from app.schemas.search import MovieSearch, MovieWithReviews
from app.services.search_service import search_movies_with_reviews


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/search", response_model=List[MovieWithReviews])
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)


@router.get("/search/", include_in_schema=False, response_model=List[MovieWithReviews])
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)


@router.get("", include_in_schema=False, response_model=List[MovieWithReviews])
def search_reviews_on_collection(title: str = Query(None)):
    if not title:
        return []
    search = MovieSearch(query=title)
    return search_movies_with_reviews(search)
