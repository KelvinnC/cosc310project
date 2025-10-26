from typing import List
from fastapi import APIRouter, Depends
from app.schemas.search import MovieSearch
from app.schemas.review import Review
from app.services.search_service import search_reviews_by_title


router = APIRouter(prefix="/searches", tags=["searches"])


@router.get("/reviews", response_model=List[Review])
def search_reviews(search: MovieSearch = Depends()):

    return search_reviews_by_title(search)

