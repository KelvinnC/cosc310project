from typing import List
from fastapi import APIRouter, Query
from app.schemas.review import Review
from app.schemas.search import MovieSearch
from app.services.search_service import search_reviews_by_title


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/search", response_model=List[Review])
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_reviews_by_title(search)


@router.get("/search/", response_model=List[Review], include_in_schema=False)
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    return search_reviews_by_title(search)


@router.get("", response_model=List[Review], include_in_schema=False)
def search_reviews_on_collection(title: str = Query(None)):
    if not title:
        return []
    search = MovieSearch(query=title)
    return search_reviews_by_title(search)

