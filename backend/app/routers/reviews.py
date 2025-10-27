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

