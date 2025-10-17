from fastapi import APIRouter, status
from typing import List
from schemas.movie import Movie, MovieCreate, MovieUpdate
from services.movie_service import list_movies, create_movie, delete_movie, update_movie

router = APIRouter(prefix="/movies", tags=["movies"])

@router.get("", response_model=List[Movie])
def get_movies():
    return list_movies()

@router.post("", response_model=Movie, status_code=201)
def post_movie(payload: MovieCreate):
    return create_movie(payload)

from services.movie_service import list_movies, create_movies, get_movie_by_id

@router.get("/{movie_id}", response_model=Movie)
def get_movie(movie_id: str):
    return get_movie_by_id(movie_id)

@router.put("/{movie_id}", response_model=Movie)
def put_movie(movie_id: str, payload: MovieUpdate):
    return update_movie(movie_id, payload)

@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_movie(movie_id: str):
    delete_movie(movie_id)
    return None