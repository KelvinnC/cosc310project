from fastapi import APIRouter, status, Query, HTTPException
from typing import List
from app.schemas.movie import Movie, MovieCreate, MovieUpdate, MovieWithReviews, MovieSummary
from app.services.movie_service import (
    list_movies,
    create_movie,
    delete_movie,
    update_movie,
    get_movie_by_id,
    search_movies_titles,
    movie_summary_by_id,
)
 

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[Movie])
def get_movies(sort_by: str | None = Query(None), order: str = Query("asc")):
    return list_movies(sort_by=sort_by, order=order)

@router.post("", response_model=Movie, status_code=201)
def post_movie(payload: MovieCreate):
    return create_movie(payload)

@router.get("/search", response_model=List[MovieSummary])
def search_movies(title: str = Query(..., min_length=1)):
    return search_movies_titles(title)

@router.get("/search/", include_in_schema=False, response_model=List[MovieSummary])
def search_movies_slash(title: str = Query(..., min_length=1)):
    return search_movies_titles(title)

@router.get("/{movie_id}", response_model=List[MovieWithReviews])
def get_movie(movie_id: str):
    try:
        return [get_movie_by_id(movie_id)]
    except HTTPException as exc:
        if getattr(exc, "status_code", None) == 404:
            return []
        raise

@router.put("/{movie_id}", response_model=Movie)
def put_movie(movie_id: str, payload: MovieUpdate):
    return update_movie(movie_id, payload)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie(movie_id: str):
    delete_movie(movie_id)
    return None
