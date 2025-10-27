from typing import List
from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
import json
from app.schemas.search import MovieSearch
from app.schemas.review import Review
from app.services.search_service import iter_all_matching_reviews


router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/search", response_model=List[Review], response_class=StreamingResponse)
def search_reviews(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    def stream():
        yield "["
        first = True
        for obj in iter_all_matching_reviews(search):
            if not first:
                yield ","
            else:
                first = False
            yield json.dumps(obj)
        yield "]"
    return StreamingResponse(stream(), media_type="application/json")


@router.get("/search/", include_in_schema=False, response_model=List[Review], response_class=StreamingResponse)
def search_reviews_slash(title: str = Query(..., min_length=1)):
    search = MovieSearch(query=title)
    def stream():
        yield "["
        first = True
        for obj in iter_all_matching_reviews(search):
            if not first:
                yield ","
            else:
                first = False
            yield json.dumps(obj)
        yield "]"
    return StreamingResponse(stream(), media_type="application/json")


@router.get("", include_in_schema=False, response_model=List[Review], response_class=StreamingResponse)
def search_reviews_on_collection(title: str = Query(None)):
    if not title:
        return []
    search = MovieSearch(query=title)
    def stream():
        yield "["
        first = True
        for obj in iter_all_matching_reviews(search):
            if not first:
                yield ","
            else:
                first = False
            yield json.dumps(obj)
        yield "]"
    return StreamingResponse(stream(), media_type="application/json")
