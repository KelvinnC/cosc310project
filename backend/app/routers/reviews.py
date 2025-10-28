from typing import List
from fastapi import APIRouter, Query
from app.schemas.search import MovieSearch
from app.schemas.review import Review
from app.services.search_service import all_matching_reviews


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/search", response_model=List[Review])
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return all_matching_reviews(search)


@router.get("/search/", include_in_schema=False, response_model=List[Review])
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return all_matching_reviews(search)


@router.get("", include_in_schema=False, response_model=List[Review])
def search_reviews_on_collection(title: str = Query(None)):
    if not title:
        return []
    search = MovieSearch(query=title)
    return all_matching_reviews(search)
